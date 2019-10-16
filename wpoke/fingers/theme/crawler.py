import asyncio
import itertools
import re
from dataclasses import dataclass
from io import StringIO
from typing import List, Optional, Set, Iterator, Union

import aiohttp
from aiohttp import ClientSession
from lxml import etree

from wpoke import exceptions as general_exceptions
from wpoke.conf import settings
from wpoke.exceptions import ThemePathMissingException, BundledThemeException
from wpoke.store import peek_store
from wpoke.validators.url import validate_url
from .models import WPThemeMetadata, WPThemeModelDisplay


def raise_on_failure(status_code: int, has_body: bool) -> None:
    if 400 <= status_code < 500:
        # Some 4XX responses are served by WordPress, therefore still
        # prone to yield interesting data
        if not has_body:
            raise general_exceptions.TargetNotFound
    elif status_code > 499:
        raise general_exceptions.TargetInternalServerError


def extract_info_from_css(css_content: str) -> WPThemeMetadata:
    """ Extract css theme metadata into WPThemeMetadata model
    :param css_content: raw style.css content
    :return: WPThemeMetadata
    """
    any_match = False
    wp_meta = WPThemeMetadata()
    css_content = css_content.replace("\r", "\n")

    for k, v in WPThemeModelDisplay():
        # https://github.com/WordPress/WordPress/blob/aab929b8d619bde14495a97cdc1eb7bdf1f1d487/wp-includes/functions.php#L5182
        regex_ = f"^[ \t/*#@]*{v}:(?P<meta_value>.*)$"
        regex = re.compile(regex_, re.IGNORECASE | re.M)
        match = re.search(regex, css_content)

        if match:
            meta_value = match.group("meta_value").strip()
            wp_meta.set_value_for_key(k, meta_value)
            any_match = True

    if not any_match:
        raise BundledThemeException

    return wp_meta


def truncate_theme_url(url: str) -> str:
    """
    :param url: Full url containing the /wp-content/themes sub string
    :return: url from protocol scheme to theme name
    """
    regex = re.compile(r".*/wp-content/themes/[_\-\w+\.]+/")
    return regex.search(url).group()


def remove_duplicated_theme_urls(urls: Union[List[str], Iterator[str]]) -> Set[str]:
    """
    :param urls: All urls containing /wp-content/themes/
    :return: set of unique urls from protocol scheme to theme name
    """
    return {truncate_theme_url(url) for url in urls}


def extract_theme_path_candidates(url: str, html: str) -> Optional[List[str]]:
    """ Scrapes all possible urls in a html document potentially
        disclosing available active themes
    :param url: Target website
    :param html: Content body of the response of url (Redirects are followed)
    :raises: MalformedBodyException
    :return: list of candidate urls, gathered by different engines:
        - URLs present on either <link> or <script> tags
        - URLs present in the document, including comments. Sometimes, theme
            information is left as debugging info by the developer or displayed
            by the theme creator intentionally.
    """

    html = html.strip()
    if not html:
        return None

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser)

    if tree is None:
        return None

    xpath_candidates = [
        '//link[contains(@href, "/wp-content/themes/")]/@href',
        '//script[contains(@src, "/wp-content/themes/")]/@src',
    ]

    # TODO: Check that candidate urls start with the same domain as the
    # supplied url!

    # tree.xpath returns a list of string values matching the path.
    # A single list of them is created and then converted to a set.
    matches = [tree.xpath(xpath) for xpath in xpath_candidates]
    matches_flat = itertools.chain.from_iterable(matches)

    candidates = list(remove_duplicated_theme_urls(matches_flat))

    if candidates:
        return candidates

    # As a last resort, search by regex in comments. Some themes leave
    # tracks of the theme name as html comments deliberately.

    # TODO: Somehow, mark this result as less valid as any other extracted
    # from DOM elements.
    return extract_theme_path_by_global_regex(url, html)


def extract_theme_path_by_global_regex(url: str, html: str) -> Optional[List[str]]:
    """ Performs a cross text search in the document, ignoring markup. """
    regex_str = r"(?://|https?)(?:.*?)/wp-content/themes/[\d\w\-_]+/"
    regex = re.compile(regex_str, re.IGNORECASE)
    result = re.findall(regex, html)

    if result is None:
        return list()

    return [match for match in result if validate_url.is_same_origin(match, url)]


@dataclass
class WPThemeMetadataConfiguration:
    timeout: int = settings.timeout
    user_agent: str = settings.user_agent
    max_redirects: int = settings.max_redirects
    ssl_enabled: bool = settings.ssl_enabled


class WPThemeMetadataCrawler:
    def __init__(
        self,
        http_session: ClientSession,
        http_config: Optional[WPThemeMetadataConfiguration] = None,
    ):
        self.session = http_session
        self.http_config = http_config or WPThemeMetadataConfiguration()
        self.store = peek_store()

    @property
    def request_options(self):
        return dict(
            ssl=self.http_config.ssl_enabled,
            timeout=self.http_config.timeout,
            max_redirects=self.http_config.max_redirects,
            headers={"User-Agent": self.http_config.user_agent},
        )

    async def _do_request(self, target_url: str, http_method: str = "GET"):
        async with self.session.request(
            method=http_method.lower(), url=target_url, **self.request_options
        ) as response:
            body = await response.text()
            return response.status, body

    async def fetch_html_body(self, url: str):
        if self.store.has("INDEX_BODY"):
            return self.store.INDEX_BODY
        status, body = await self._do_request(url, "GET")
        raise_on_failure(status_code=status, has_body=bool(body))
        self.store.INDEX_BODY = body
        return body

    async def fetch_style_css(self, url: str):
        status, css_content = await self._do_request(url, "GET")
        css_length = len(css_content)
        raise_on_failure(status_code=status, has_body=bool(css_content))
        # https://github.com/WordPress/WordPress/blob/aab929b8d619bde14495a97cdc1eb7bdf1f1d487/wp-includes/functions.php#L5156
        return css_content[: (8192 if css_length >= 8192 else css_length)]

    async def get_screenshot(self, url: str) -> Optional[str]:
        """ Received a curated URL to a theme and returns theme
        screenshot image path if any """
        for img_candidate_extension in ["jpeg", "png", "jpg"]:
            screenshot_url = f"{url}screenshot.{img_candidate_extension}"
            status, _ = await self._do_request(screenshot_url, "HEAD")
            if 200 <= status <= 299:
                return screenshot_url
        return None

    async def add_extra_features(
        self, url: str, model: WPThemeMetadata
    ) -> WPThemeMetadata:
        # Screenshot feature
        screenshot = await self.get_screenshot(url)
        if screenshot:
            model.set_featured_image(screenshot)
        return model

    async def get_theme(self, url: str) -> List[WPThemeMetadata]:
        try:
            html_content = await self.fetch_html_body(url)

            if not html_content:
                raise general_exceptions.MalformedBodyException

            candidates = extract_theme_path_candidates(url, html_content)

            if not candidates:
                raise ThemePathMissingException

            theme_models = []

            for candidate_url in candidates:
                style_css_path = candidate_url + "style.css"
                css_content = await self.fetch_style_css(style_css_path)

                try:
                    theme_model = extract_info_from_css(css_content)
                except BundledThemeException:
                    continue
                else:
                    theme_model = await self.add_extra_features(
                        candidate_url, theme_model
                    )
                    theme_models.append(theme_model)

            if len(theme_models) < 1:
                # At least one css model should be found.
                raise BundledThemeException

            return theme_models
        except aiohttp.client.TooManyRedirects:
            raise general_exceptions.NastyTargetException
        except aiohttp.client.ClientConnectionError as e:
            raise general_exceptions.TargetConnectionError() from e
        except aiohttp.ServerTimeoutError:
            raise general_exceptions.TargetTimeout
        except aiohttp.client.ClientError:
            # General unexpected error
            raise general_exceptions.TargetInternalServerError
        except asyncio.TimeoutError as e:
            raise general_exceptions.TargetTimeout from e

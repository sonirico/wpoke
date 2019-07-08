import asyncio
import itertools
import re
from typing import List, Optional, Set, Iterator, Union

import aiohttp
from aiohttp import ClientSession
from lxml import etree

from wpoke import exceptions as general_exceptions
from wpoke.conf import HTTPSettings
from wpoke.validators.url import validate_url
from .exceptions import *
from .models import WPThemeMetadata, WPThemeModelDisplay


def raise_on_failure(status_code: int, has_body: bool) -> None:
    if 400 <= status_code < 500:
        # Some 4XX responses are served by WordPress, therefore still
        # prone to yield interesting data
        if not has_body:
            raise general_exceptions.TargetNotFound
    elif status_code > 499:
        raise general_exceptions.TargetInternalServerError


async def fetch_html_body(session: ClientSession, url: str, **request_config):
    """ Encapsulates request/response lifecycle management

    :param session:
    :param url:
    :param params:
    :return:
    """
    async with session.get(url, **request_config) as response:
        body = await response.text()

        raise_on_failure(response.status, bool(body))

        return body


async def fetch_style_css(session: ClientSession, url: str, **params):
    async with session.get(url, **params) as response:
        body = await response.text()
        body_length = len(body) if body else 0

        raise_on_failure(response.status, bool(body_length))

        # https://github.com/WordPress/WordPress/blob/aab929b8d619bde14495a97cdc1eb7bdf1f1d487/wp-includes/functions.php#L5156
        return body[:(8192 if body_length >= 8192 else body_length)]


def extract_info_from_css(css_content: str) -> WPThemeMetadata:
    """ Extract css theme metadata into WPThemeMetadata model
    :param css_content: raw style.css content
    :return: WPThemeMetadata
    """
    any_match = False
    wp_meta = WPThemeMetadata()
    css_content = css_content.replace('\r', '\n')

    for k, v in WPThemeModelDisplay():
        regex_ = f"^[ \t/*#@]*{v}:(?P<meta_value>.*)$"  # https://github.com/WordPress/WordPress/blob/aab929b8d619bde14495a97cdc1eb7bdf1f1d487/wp-includes/functions.php#L5182
        regex = re.compile(regex_, re.IGNORECASE | re.M)
        match = re.search(regex, css_content)

        if match:
            meta_value = match.group('meta_value').strip()
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
    regex = re.compile(r'.*/wp-content/themes/[_\-\w+]+/')
    return regex.search(url).group()


def remove_duplicated_theme_urls(urls: Union[List[str],
                                             Iterator[str]]) -> Set[str]:
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

    tree = etree.HTML(html)

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


def extract_theme_path_by_global_regex(url: str,
                                       html: str) -> Optional[List[str]]:
    """ Performs a cross text search in the document, ignoring markup. """
    regex = re.compile(r'(?://|https?)(?:.*?)/wp-content/themes/[\d\w\-_]+/',
                       re.IGNORECASE)
    result = re.findall(regex, html)

    if result is None:
        return list()

    return [match for match in result
            if validate_url.is_same_origin(match, url)]


async def get_screenshot(session: ClientSession, url: str,
                         **http_settings) -> Optional[str]:
    for img_candidate_extension in ['jpeg', 'png', 'jpg']:
        screenshot_url = f'{url}screenshot.{img_candidate_extension}'

        async with session.head(screenshot_url,
                                **http_settings) as response:
            if 200 <= response.status <= 299:
                return screenshot_url
    return None


async def add_extra_features(session, url: str,
                             model: WPThemeMetadata,
                             **http_settings) -> WPThemeMetadata:
    # Screenshot feature
    screenshot = await get_screenshot(session, url, **http_settings)
    if screenshot:
        model.set_featured_image(screenshot)
    return model


async def get_theme(url: str, options: HTTPSettings,
                    session: ClientSession) -> List[WPThemeMetadata]:
    http_settings = options.request_config
    try:
        html_content = await fetch_html_body(session, url,
                                             **http_settings)

        if not html_content:
            raise general_exceptions.MalformedBodyException

        candidates = extract_theme_path_candidates(url, html_content)

        if not candidates:
            raise ThemePathMissingException

        theme_models = []

        for candidate_url in candidates:
            style_css_path = candidate_url + 'style.css'
            css_content = await fetch_style_css(session,
                                                style_css_path,
                                                **http_settings)

            try:
                theme_model = extract_info_from_css(css_content)
            except BundledThemeException:
                continue
            else:
                theme_model = await add_extra_features(session,
                                                       candidate_url,
                                                       theme_model,
                                                       **http_settings)
                theme_models.append(theme_model)

        if len(theme_models) < 1:
            # At least one css model must be found.
            raise BundledThemeException

        return theme_models
    except aiohttp.client.TooManyRedirects:
        raise general_exceptions.NastyTargetException
    except aiohttp.client.ClientConnectionError:
        raise general_exceptions.TargetInternalServerError
    except aiohttp.ServerTimeoutError:
        raise general_exceptions.TargetTimeout
    except aiohttp.client.ClientError:
        # General unexpected error
        raise general_exceptions.TargetInternalServerError
    except asyncio.TimeoutError as e:
        raise general_exceptions.TargetTimeout from e

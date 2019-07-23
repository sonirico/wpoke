import unittest

import pytest
from asynctest import CoroutineMock

import wpoke.exceptions
from wpoke.fingers.theme.crawler import WPThemeMetadataCrawler
from wpoke.fingers.theme.crawler import extract_info_from_css
from wpoke.fingers.theme.crawler import extract_theme_path_candidates
from wpoke.fingers.theme.crawler import remove_duplicated_theme_urls
from wpoke.fingers.theme.crawler import truncate_theme_url


@pytest.mark.asyncio
async def test_get_screenshot():
    session = CoroutineMock()
    session.request.return_value.__aenter__.return_value.status = 200
    session.request.return_value.__aenter__.return_value.text = CoroutineMock()
    crawler = WPThemeMetadataCrawler(http_session=session)
    payload = 'http://wpoke.app/wp-content/themes/hola/'
    actual = await crawler.get_screenshot(payload)
    expected = f'{payload}screenshot.jpeg'
    assert actual == expected


@pytest.mark.parametrize("actual, expected", [
    ('http://un-dominio.es/wp-content/themes/twelve/plugins/jquery.min.js',
     'http://un-dominio.es/wp-content/themes/twelve/'),

    ('http://otro-dominio.es/wp-content/themes/fifteen/',
     'http://otro-dominio.es/wp-content/themes/fifteen/'),

    ('http://y-otro-dominio.mas/wp-content/themes/fifteen/style.css',
     'http://y-otro-dominio.mas/wp-content/themes/fifteen/'),
])
def test_truncate_url(actual, expected):
    assert truncate_theme_url(actual) == expected


@pytest.mark.parametrize("urls, expected", [
    (
            [
                'http://wpoke.app/wp-content/themes/pepe/jquery.js',
                'http://wpoke.app/wp-content/themes/paco/jquery.js',
                'http://wpoke.app/wp-content/themes/paco/plugins/ui/widget.js',
                'http://wpoke.app/wp-content/themes/pepe/style.css'
            ],
            {
                'http://wpoke.app/wp-content/themes/pepe/',
                'http://wpoke.app/wp-content/themes/paco/'
            }
    )
])
def test_remove_duplicated_urls(urls, expected):
    actual = remove_duplicated_theme_urls(urls)
    unittest.TestCase().assertSetEqual(actual, expected)


@pytest.mark.usefixtures('fixture_file_content', autouse=True)
class TestThemeCrawlerExtractInfoFromCSS(unittest.TestCase):
    def test_extract_css_info_normal(self):
        mocked_css = self.fixture_content('crawlers/theme/css/normal.css')

        wp_metadata = extract_info_from_css(mocked_css)

        assert 'Baskerville' == wp_metadata.theme_name
        assert 'baskerville' == wp_metadata.text_domain
        assert '1.19' == wp_metadata.version
        assert 'A beautiful, responsive ...' == wp_metadata.description

    def test_extract_css_info_empty(self):
        mocked_css = self.fixture_content('crawlers/theme/css/empty.css')

        with self.assertRaises(wpoke.exceptions.BundledThemeException):
            extract_info_from_css(mocked_css)

    def test_extract_css_info_duplicated_fetchs_first_match(self):
        mocked_css = self.fixture_content('crawlers/theme/css/duplicated.css')

        wp_metadata = extract_info_from_css(mocked_css)

        assert 'Baskerville' == wp_metadata.theme_name
        assert 'baskerville' == wp_metadata.text_domain

    def test_empty_value_does_not_fallback_to_next(self):
        mocked_css = self.fixture_content(
            'crawlers/theme/css/empty_next_fallback.css')

        wp_metadata = extract_info_from_css(mocked_css)

        assert 'Divi' == wp_metadata.theme_name
        assert wp_metadata.author is ''
        assert wp_metadata.author_uri == 'divi.com'


@pytest.mark.usefixtures('fixture_file_content', autouse=True)
class TestThemeCrawlerExtractCandidateURLs(object):
    def test_extract_candidate_theme_urls_ok(self):
        mocked_html = self.fixture_content('crawlers/theme/html/normal.html')
        target_url = 'https://normal.wp.com/'
        actual = extract_theme_path_candidates(target_url, mocked_html)
        expected = [
            "https://normal.wp.com/wp-content/themes/baskerville/",
        ]

        for expected_url in expected:
            assert expected_url in actual

    def test_extract_candidate_urls_have_not_duplicates(self):
        mocked_html = self.fixture_content(
            'crawlers/theme/html/duplicates.html')
        target_url = 'https://duplicates.wp.com/'

        actual = extract_theme_path_candidates(target_url, mocked_html)
        expected = [
            "https://duplicates.wp.com/wp-content/themes/baskerville/",
        ]

        for expected_url in expected:
            assert expected_url in actual

    def test_extract_candidate_urls_from_empty_response(self):
        mocked_html = self.fixture_content('crawlers/theme/html/empty.html')
        target_url = 'http://vacuum.io/'

        actual = extract_theme_path_candidates(target_url, mocked_html)
        expected = None

        assert expected == actual

    def test_extract_candidate_urls_from_malformed_response(self):
        mocked_html = self.fixture_content('crawlers/theme/html/malformed.html')
        target_url = 'http://ijustbornlikethis.es'

        actual = extract_theme_path_candidates(target_url, mocked_html)
        expected = []

        assert 0 == len(actual)
        assert expected == actual

    def test_extract_candidate_urls_from_non_text_response(self):
        mocked_html = self.fixture_content('crawlers/theme/html/binary.html')
        target_url = 'http://aoneorazero.com'

        actual = extract_theme_path_candidates(target_url, mocked_html)
        expected = []

        assert 0 == len(actual)
        assert expected == actual

    def test_extracted_urls_same_domain(self):
        mocked_html = self.fixture_content(
            'crawlers/theme/html/urls_third_parties.html')
        target_url = 'https://wp.com/whatever/goes/here/'

        actual = extract_theme_path_candidates(target_url, mocked_html)
        expected = ['https://wp.com/wp-content/themes/millionparsecs/']

        assert 1 == len(actual)

        for expected_token in expected:
            assert expected_token in actual

    def test_extract_candidate_urls_child_theme_installed(self):
        mocked_html = self.fixture_content(
            'crawlers/theme/html/child_theme.html')
        target_url = 'https://wp.com'
        actual = extract_theme_path_candidates(target_url, mocked_html)
        expected = [
            "https://wp.com/wp-content/themes/baskerville/",
            "https://wp.com/wp-content/themes/baskerville-child-001/"
        ]

        for expected_uri in expected:
            assert expected_uri in actual

    def test_extract_candidate_urls_from_global_cross_search(self):
        mocked_html = self.fixture_content(
            'crawlers/theme/html/sites/sozpic.com.html')
        target_url = 'https://www.sozpic.com'
        actual = extract_theme_path_candidates(target_url, mocked_html)
        expected = [
            "https://www.sozpic.com/wp-content/themes/mana/"
        ]

        for expected_uri in expected:
            assert expected_uri in actual

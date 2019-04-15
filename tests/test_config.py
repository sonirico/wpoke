import unittest

from wpoke.conf import DEFAULT_CONFIG
from wpoke.conf import Settings


class TestSettingsSetAttribute(unittest.TestCase):
    def test_configure_normal(self):
        settings = Settings()
        settings['timeout'] = 10
        self.assertEqual(10, settings.timeout)


class TestSettingsGetAttributes(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(DEFAULT_CONFIG)

    def test_settings_initialized(self):
        expected_timeout = DEFAULT_CONFIG['TIMEOUT']
        actual_timeout = self.settings['TIMEOUT']
        self.assertEqual(expected_timeout, actual_timeout)

    def test_settings_can_be_accessed_by_attrs_lowercase(self):
        expected_timeout = DEFAULT_CONFIG['TIMEOUT']
        actual_timeout = self.settings.timeout
        self.assertEqual(expected_timeout, actual_timeout)

    def test_settings_can_be_accessed_by_attrs_uppercase(self):
        expected_timeout = DEFAULT_CONFIG['TIMEOUT']
        actual_timeout = self.settings.TIMEOUT
        self.assertEqual(expected_timeout, actual_timeout)

    def test_settings_non_existent_key_raises_attribute_error(self):
        self.assertRaises(AttributeError, lambda: self.settings.FAKE)

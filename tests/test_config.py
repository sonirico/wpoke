import unittest
from contextvars import ContextVar

from wpoke.conf import SettingAttr


class TestSettings:
    test_key = SettingAttr('test_key_b', ContextVar('no_test', default=1))


class TestSettingsSetAttribute(unittest.TestCase):
    def test_context_var_can_accessed_from_dict_and_data_descriptor(self):
        settings = TestSettings()
        self.assertEqual(settings.test_key, settings.test_key_b.get())

    def test_context_var_can_be_set_from_dict_and_data_descriptor(self):
        settings = TestSettings()
        settings.test_key = 2
        self.assertEqual(2, settings.test_key)
        self.assertEqual(settings.test_key, settings.test_key_b.get())

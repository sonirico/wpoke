from unittest import TestCase

from wpoke.exceptions import DataStoreAttributeNotFound
from wpoke.store import DataStore


class StoreTestCase(TestCase):
    def setUp(self):
        self.store = DataStore()

    def tearDown(self):
        self.store.clear()

    def assert_getattr_equals(self, expected_value, actual_key):
        try:
            actual_value = getattr(self.store, actual_key)
        except AttributeError:
            self.fail(f"Expected store to have key '{actual_key}'")
        else:
            if expected_value != actual_value:
                self.fail(f"Expected store to have value '{expected_value}' "
                          f"for key '{actual_key}'")

    def assert_attribute_equals(self, expected, key_name):
        self.assert_getattr_equals(expected, key_name.upper())
        self.assert_getattr_equals(expected, key_name.lower())

    def test_getattribute(self):
        expected_version = "4.9.10"
        self.store['WP_VERSION'] = expected_version
        self.assert_attribute_equals(expected_version, 'WP_VERSION')

    def test_get_or_set_returns_get(self):
        expected_version = "4.9.10"
        self.store['WP_VERSION'] = expected_version
        actual_version = self.store.get_or_set('WP_VERSION', "5.1.0")
        self.assertEqual(expected_version, actual_version)

    def test_get_or_raise(self):
        self.assertRaises(DataStoreAttributeNotFound,
                          self.store.get_or_raise,
                          "WP_VERSION")

    def test_get_safe_return_none(self):
        self.assertIsNone(self.store.get_safe("non_existent_key"))

    def test_get_safe_return_data(self):
        expected_value = "value"
        self.store["non_existent_key"] = expected_value
        self.assertEqual(expected_value,
                         self.store.get_safe("non_existent_key"))

    def test_get_or_set_returns_set(self):
        expected_version = "4.9.10"
        # self.store['WP_VERSION'] = "whatever"
        actual_version = self.store.get_or_set('WP_VERSION',
                                               expected_version)
        self.assertEqual(expected_version, actual_version)

    def test_set_lazy(self):
        expected_version = "4.9.10"
        self.store['WP_VERSION'] = expected_version
        self.store.set_lazy('WP_VERSION', "5.1.0")
        self.assert_attribute_equals(expected_version, "WP_VERSION")

    def test_set(self):
        expected_version = "4.9.10"
        self.store['WP_VERSION'] = "I should be overridden"
        self.store.set('WP_VERSION', expected_version)
        self.assert_attribute_equals(expected_version, "WP_VERSION")

    def test_keys(self):
        expected_keys = ["A", "B", "Z"]
        self.store['Z'] = ""
        self.store['A'] = ""
        self.store['B'] = ""
        self.assertListEqual(expected_keys, self.store.keys())

    def test_delete_key_not_exist_should_not_raise_key_error(self):
        del self.store['WP_VERSION']
        self.store.delete("WP_VERSION")

    def test_delete_key_does_exist(self):
        self.store['WP_VERSION'] = "whatever"
        self.store.delete("WP_VERSION")
        self.assertRaises(KeyError,
                          lambda: self.store['WP_VERSION'])

    def test_clear(self):
        self.store['Z'] = ""
        self.store['A'] = ""
        self.store['B'] = ""
        self.assertEqual(3, len(self.store.keys()))
        self.store.clear()
        self.assertEqual(0, len(self.store.keys()))

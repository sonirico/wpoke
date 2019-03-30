import unittest

from wpoke.fingers.theme import WPThemeMetadata


class TestWPThemeMetadata(unittest.TestCase):
    def test_serialize_empty_values(self):
        w = WPThemeMetadata()

        w_serialized = w.serialize()

        self.assertIsInstance(w_serialized['tags'], list)
        self.assertIsNone(w_serialized['theme_name'])

    def test_serialize_tags_field(self):
        w = WPThemeMetadata()

        w.tags = 'hacking, programming  , devops'

        w_serialized = w.serialize()

        self.assertListEqual(w_serialized['tags'], ['hacking', 'programming',
                                                    'devops'])

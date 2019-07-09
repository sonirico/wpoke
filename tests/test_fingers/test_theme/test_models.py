import unittest

from wpoke.fingers.theme.models import WPThemeMetadata
from wpoke.fingers.theme.serializers import WPThemeMetadataSerializer


class TestWPThemeMetadata(unittest.TestCase):
    def test_serialize_empty_values(self):
        wp_metadata_model = WPThemeMetadata()
        serializer = WPThemeMetadataSerializer(wp_metadata_model)
        w_serialized = serializer.data

        self.assertIsInstance(w_serialized['tags'], list)
        self.assertIsNone(w_serialized['theme_name'])

    def test_serialize_tags_field(self):
        wp_metadata_model = WPThemeMetadata()
        wp_metadata_model.tags = 'hacking, programming  , devops'

        serializer = WPThemeMetadataSerializer(wp_metadata_model)
        w_serialized = serializer.data

        self.assertListEqual(w_serialized['tags'], ['hacking', 'programming',
                                                    'devops'])

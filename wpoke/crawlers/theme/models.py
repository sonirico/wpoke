import serpy

from copy import copy

from typing import ValuesView


class WPThemeMetadataSerializer(serpy.Serializer):
    theme_name = serpy.StrField(required=False)
    theme_uri = serpy.StrField(required=False)
    description = serpy.StrField(required=False)
    author = serpy.StrField(required=False)
    author_uri = serpy.StrField(required=False)
    version = serpy.StrField(required=False)
    license = serpy.StrField(required=False)
    license_uri = serpy.StrField(required=False)
    tags = serpy.MethodField(required=False)
    text_domain = serpy.StrField(required=False)
    template = serpy.StrField(required=False)
    featured_image = serpy.StrField(required=False)

    def get_tags(self, obj) -> list:
        if obj.tags:
            return [w.strip() for w in obj.tags.split(',') if w.strip()]
        return []


class WPThemeMetadata(object):
    schema_data = {
        'theme_name': 'Theme Name',
        'theme_uri': 'Theme URI',
        'description': 'Description',
        'author': 'Author',
        'author_uri': 'Author URI',
        'version': 'Version',
        'license': 'License',
        'license_uri': 'License URI',
        'tags': 'Tags',
        'text_domain': 'Text Domain',
        'included_translations': 'Included Translations',
        'template': 'Template',
        'status': 'Status'
    }

    def __init__(self, **metadata) -> None:
        self.theme_name = metadata.get('theme_name')
        self.theme_uri = metadata.get('theme_uri')
        self.description = metadata.get('description')
        self.author = metadata.get('author')
        self.author_uri = metadata.get('author_uri')
        self.version = metadata.get('version')
        self.license = metadata.get('license')
        self.license_uri = metadata.get('license_uri')
        self.tags = metadata.get('tags')
        self.text_domain = metadata.get('text_domain')
        self.template = metadata.get('template')
        self.status = metadata.get('status')
        self.featured_image = metadata.get('screenshot')

    @classmethod
    def get_metadata_schema(cls) -> dict:
        return copy(cls.schema_data)

    @classmethod
    def get_metadata_display_values(cls) -> ValuesView[str]:
        return cls.schema_data.values()

    def set_value_for_key(self, k, v) -> None:
        setattr(self, k, v)

    def set_featured_image(self, img_link):
        self.featured_image = img_link

    def deserialize(self) -> dict:
        serializer = WPThemeMetadataSerializer(self)

        return serializer.data

from typing import List

import serpy


class WPThemeMetadataSerializer(serpy.Serializer):
    """ WPThemeModel serializes. As of now, it only performs data
        clean-up on tags
    """

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

    def get_tags(self, obj) -> List[str]:
        if not obj.tags:
            return []

        return [w.strip() for w in obj.tags.split(",") if w.strip()]

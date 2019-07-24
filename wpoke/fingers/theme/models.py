from dataclasses import dataclass
from typing import List, AnyStr


@dataclass
class WPThemeModelDisplay:
    theme_name: AnyStr = "Theme Name"
    theme_uri: AnyStr = "Theme URI"
    description: AnyStr = "Description"
    author: AnyStr = "Author"
    author_uri: AnyStr = "Author URI"
    version: AnyStr = "Version"
    license: AnyStr = "License"
    license_uri: AnyStr = "License URI"
    tags: AnyStr = "Tags"
    text_domain: AnyStr = "Text Domain"
    included_translations: AnyStr = "Included Translations"
    template: AnyStr = "Template"
    status: AnyStr = "Status"

    def __iter__(self):
        for k, v in self.__dict__.items():
            yield (k, v)


@dataclass
class WPThemeMetadata:
    theme_name: AnyStr = None
    theme_uri: AnyStr = None
    description: AnyStr = None
    author: AnyStr = None
    author_uri: AnyStr = None
    version: AnyStr = None
    license: AnyStr = None
    license_uri: AnyStr = None
    tags: List[AnyStr] = None
    text_domain: AnyStr = None
    included_translations: AnyStr = None
    template: AnyStr = None
    status: AnyStr = None
    featured_image: AnyStr = None

    def set_value_for_key(self, k, v) -> None:
        setattr(self, k, v)

    def set_featured_image(self, img_link):
        self.featured_image = img_link

import json
import sys
from typing import AnyStr, Dict, List

import wpoke.exceptions
from wpoke import exceptions as generic_exceptions
from wpoke.conf import settings, RenderFormats
from wpoke.finger import BaseFinger
from wpoke.fingers.theme.serializers import WPThemeMetadataSerializer
from . import crawler as theme_crawler


class ThemeFinger(BaseFinger):
    class Meta:
        name = "theme_metadata"

    class Cli:
        help_text = "Display themes information"
        required = False
        short_flag = "-t"
        long_flag = "--theme"

    async def run(self, target: AnyStr, **options) -> List[Dict]:
        try:
            crawler_config = theme_crawler.WPThemeMetadataConfiguration(
                timeout=settings.timeout,
                user_agent=settings.user_agent,
                max_redirects=settings.max_redirects,
            )
            crawler = theme_crawler.WPThemeMetadataCrawler(self.session, crawler_config)
            themes = await crawler.get_theme(target)
        except wpoke.exceptions.BundledThemeException as e:
            print(e.message)
        except generic_exceptions.TargetTimeout:
            timeout = settings.timeout
            print(f"Target timeout. Try to set a value higher than {timeout}")
        else:
            serializer = WPThemeMetadataSerializer(themes, many=True)
            return serializer.data

    def render(self, result, out=sys.stdout, **kwargs) -> None:
        fmt = settings.output_format
        if not fmt or fmt == RenderFormats.JSON.value:
            print(json.dumps(result, indent=4), file=out)

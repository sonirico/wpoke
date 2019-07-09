import json
import sys
from typing import AnyStr, Dict, List

from aiohttp import ClientSession

from wpoke import exceptions as generic_exceptions
from wpoke.conf import settings, RenderFormats
from wpoke.finger import BaseFinger
from wpoke.fingers.theme.serializers import WPThemeMetadataSerializer
from . import crawler as theme_crawler
from . import exceptions as theme_exceptions


class ThemeFinger(BaseFinger):
    class Meta:
        name = 'theme'

    class Cli:
        help_text = 'Display themes information'
        required = False
        short_flag = '-t'
        long_flag = '--theme'

    async def run(self,
                  target: AnyStr,
                  http_session: ClientSession,
                  **options) -> List[Dict]:
        try:
            crawler_config = theme_crawler.WPThemeMetadataConfiguration()
            crawler = theme_crawler.WPThemeMetadataCrawler(http_session,
                                                           crawler_config)
            themes = await crawler.get_theme(target)
        except theme_exceptions.BundledThemeException as e:
            print(e.message)
        except generic_exceptions.TargetTimeout:
            timeout = settings.timeout
            print(f'Target timeout. Try to set a value higher than {timeout}')
        else:
            serializer = WPThemeMetadataSerializer(themes, many=True)
            return serializer.data

    def render(self, result, out=sys.stdout, **kwargs) -> None:
        fmt = settings.output_format
        if not fmt or fmt == RenderFormats.JSON.value:
            print(json.dumps(result, indent=4), file=out)


finger_cls = ThemeFinger

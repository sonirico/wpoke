import json
import sys
from typing import AnyStr, Dict, List

from aiohttp import ClientSession

from wpoke import exceptions as generic_exceptions
from wpoke.conf import settings, RenderFormats
from wpoke.finger import BaseFinger
from . import exceptions as theme_exceptions
from .crawler import get_theme
from wpoke.fingers.theme.serializers import WPThemeMetadataSerializer


class ThemeFinger(BaseFinger):
    class Meta:
        name = 'theme'

    class Cli:
        help_text = 'Display themes information'
        required = False
        short_flag = '-t'
        long_flag = '--theme'

    async def run(self, target: AnyStr, http_session: ClientSession,
                  **options) -> List[Dict]:
        try:
            themes = await get_theme(target, http_session)
        except theme_exceptions.BundledThemeException as e:
            print(e.message)
        except generic_exceptions.TargetTimeout:
            timeout = settings.timeout
            print(f'Target timeout. Try to set a value higher than {timeout}')
        else:
            serializer = WPThemeMetadataSerializer(themes, many=True)
            return serializer.data

    def render(self, result, file=sys.stdout, **options: Settings) -> None:
        fmt = options.FORMAT
        if not fmt or fmt == RenderFormats.JSON.value:
            print(json.dumps(result, indent=4), file=file)


finger_cls = ThemeFinger

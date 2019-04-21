import json
import sys
from typing import Any, AnyStr

from aiohttp import ClientSession

from wpoke import exceptions as generic_exceptions
from wpoke.conf import HTTPSettings, Settings, RenderFormats
from wpoke.finger import BaseFinger
from . import exceptions as theme_exceptions
from .crawler import get_theme


class ThemeFinger(BaseFinger):
    class Meta:
        name = 'theme'

    class Cli:
        help_text = 'Display themes information'
        required = False
        short_flag = '-t'
        long_flag = '--theme'

    async def run(self, target: AnyStr, http_session: ClientSession,
                  **options) -> Any:
        http_settings = HTTPSettings(options)
        try:
            result = await get_theme(target, http_settings, http_session)
        except theme_exceptions.BundledThemeException as e:
            print(e.message)
        except generic_exceptions.TargetTimeout:
            timeout = http_settings.timeout
            print(f'Target timeout. Try to set a value higher than {timeout}')
        else:
            return [theme_model.serialize() for theme_model in result]

    def render(self, result, file=sys.stdout, **options: Settings) -> None:
        fmt = options.FORMAT
        if not fmt or fmt == RenderFormats.JSON.value:
            print(json.dumps(result, indent=4), file=file)


finger_cls = ThemeFinger

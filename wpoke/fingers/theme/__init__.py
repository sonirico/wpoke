import json
import sys

from wpoke import exceptions as generic_exceptions
from wpoke.finger import BaseFinger
from wpoke.loader import finger_registry

from . import exceptions as theme_exceptions
from .crawler import get_theme


@finger_registry.register
class ThemeFinger(BaseFinger):
    class Meta:
        name = 'theme'

    class Cli:
        help_text = 'Display themes information'
        required = False
        short_flag = '-t'
        long_flag = '--theme'

    async def run(self, target, timeout=None, **options):
        try:
            result = await get_theme(target, **options)
        except theme_exceptions.BundledThemeException as e:
            print(e.message)
        except generic_exceptions.TargetTimeout:
            print(f'Target timeout. Try to set a value higher than {timeout}')
        else:
            return [theme_model.serialize() for theme_model in result]

    def render(self, result, fmt=None, file=sys.stdout, **options):
        print(json.dumps(result, indent=4), file=file)

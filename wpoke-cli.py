import argparse
import asyncio
import sys
import uvloop

from wpoke.conf import Settings, DEFAULT_CONFIG
from wpoke.loader import FingerRegistry


def extract_cli_options(finger_registry):
    """
    Based on the cli options configured in every registry, load the
    pertinent settings from them
    """
    parser = argparse.ArgumentParser(
        description='WordPress information gathering tool')
    parser.add_argument('url', help='Target WordPress site. Can be any URL')
    parser.add_argument('-u', '--user-agent', type=str, dest='useragent',
                        help='User agent to use',
                        required=False)
    parser.add_argument('-f', '--format', type=str, dest='render_format',
                        help='Output format. {json|cmd}',
                        required=False)

    for lookup_key, finger in finger_registry:
        short_arg_name = getattr(finger.Cli, 'short_flag', None)
        long_arg_name = getattr(finger.Cli, 'long_flag', None)
        help_text = getattr(finger.Cli, 'help_text', None)
        required = getattr(finger.Cli, 'required', False)

        pargs = []
        pkwargs = {'dest': lookup_key, 'action': 'store_true'}

        if short_arg_name:
            pargs.append(short_arg_name)
        if long_arg_name:
            pargs.append(long_arg_name)

        if help_text:
            pkwargs['help'] = help_text
        if required is not None:
            pkwargs['required'] = required

        parser.add_argument(*pargs, **pkwargs)

    return parser.parse_args()


def load_settings(cli_options, settings):
    """
    Set global configuration based on selected options defined in the CLI
    """
    # User-Agent http header
    if cli_options.useragent:
        settings.USER_AGENT = cli_options.useragent


async def main():
    registry = FingerRegistry()
    settings = Settings(DEFAULT_CONFIG)
    registry.autodiscover_fingers(mods=settings.installed_fingers)
    cli_options = extract_cli_options(registry)
    load_settings(cli_options, settings)
    poke_result = {}

    # Perform remote lookups and obtain data
    for p_lookup_name, plugin in registry:
        plugin_result = await plugin.run(cli_options.url, **settings)
        poke_result[p_lookup_name] = plugin_result

    # Iterate over fingers again so as to render data
    for p_lookup_name, plugin in registry:
        plugin.render(poke_result[p_lookup_name], **settings)


if __name__ == '__main__':
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        loop = asyncio.get_event_loop()

        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        sys.exit(0)

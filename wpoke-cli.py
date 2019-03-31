import argparse
import asyncio
import sys
import uvloop

from wpoke.conf import configure, settings
from wpoke.loader import finger_registry


def get_cli_options():
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


def load_settings(cli_options):
    # User-Agent http header
    if cli_options.useragent:
        configure('useragent', cli_options.useragent)


def load_plugins():
    finger_registry.autodiscover_fingers(mods=settings.installed_fingers)


def load_plugin_options():
    pass


async def main():
    load_plugins()
    load_plugin_options()
    cli_options = get_cli_options()
    load_settings(cli_options)
    poke_result = {}

    settings_dict = settings.as_dict()

    for p_lookup_name, plugin in finger_registry:
        plugin_result = await plugin.run(cli_options.url, **settings_dict)
        poke_result[p_lookup_name] = plugin_result

    for p_lookup_name, plugin in finger_registry:
        plugin.render(poke_result[p_lookup_name], **settings_dict)


if __name__ == '__main__':
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        loop = asyncio.get_event_loop()

        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        sys.exit(0)

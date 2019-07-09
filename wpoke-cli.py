#!/usr/bin/env python

import argparse
import asyncio
import contextvars as ctxv
import sys

import uvloop
from aiohttp import ClientSession

from wpoke.conf import InvalidCliConfigurationException, settings
from wpoke.loader import FingerRegistry
from wpoke.fingers.theme import ThemeFinger


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
    parser.add_argument('-tt', '--timeout', type=str, dest='timeout',
                        help='Global default timeout for all requests',
                        required=False)
    parser.add_argument('-f', '--format', type=str, dest='render_format',
                        help='Output format. {json|cli}',
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

    return parser, parser.parse_args()


def load_settings(cli_options):
    """
    Set global configuration based on selected options defined in the CLI
    """
    # User-Agent http header
    if cli_options.useragent:
        settings.USER_AGENT = cli_options.useragent
    # Global timeout
    if cli_options.timeout:
        settings.TIMEOUT = cli_options.timeout
    # Output format
    if cli_options.render_format:
        if cli_options.render_format not in settings.ALLOWED_FORMATS:
            message = f'unknown format: {cli_options.render_format}'
            raise InvalidCliConfigurationException(message)
        settings.FORMAT = cli_options.render_format


async def main():
    registry = FingerRegistry()
    registry.register('theme', ThemeFinger)
    # registry.autodiscover_fingers()
    cli_parser, cli_options = extract_cli_options(registry)

    try:
        load_settings(cli_options)
    except InvalidCliConfigurationException as e:
        print(str(e))
        cli_parser.print_help()
        sys.exit(2)

    poke_result = {}

    # TODO: Abstract away plugin orchestration as running them concurrently
    # may cause server alarms go off

    async with ClientSession() as session:
        # Perform remote lookups and obtain data
        for p_lookup_name, plugin in registry:
            plugin_result = await plugin.run(cli_options.url,
                                             session)
            poke_result[p_lookup_name] = plugin_result

    # Iterate over fingers again so as to render data
    for p_lookup_name, plugin in registry:
        plugin.render(poke_result[p_lookup_name])


if __name__ == '__main__':
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        loop = asyncio.get_event_loop()

        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        sys.exit(0)

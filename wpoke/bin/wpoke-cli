#!/usr/bin/env python

import argparse
import asyncio
import json
import sys

import wpoke
from aiohttp import ClientSession

from wpoke.conf import InvalidCliConfigurationException, settings
from wpoke.fingers import ThemeFinger
from wpoke.hand import Hand
from wpoke.models import HandResultSerializer
from wpoke.store import push_store, DataStore


def extract_cli_options(hand: Hand):
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
    parser.add_argument('-r', '--max-redirects', type=str, dest='max_redirects',
                        help='Global default max redirects for each HTTP call',
                        required=False)
    parser.add_argument('-f', '--format', type=str, dest='render_format',
                        help='Output format. {json|cli}',
                        required=False)

    for lookup_key, finger in hand.registered_fingers:
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
        settings.user_agent = cli_options.useragent
    # Global timeout
    if cli_options.timeout:
        settings.timeout = int(cli_options.timeout)
    # Global max redirects
    if cli_options.max_redirects:
        settings.max_redirects = int(cli_options.max_redirects)
    # Output format
    if cli_options.render_format:
        if cli_options.render_format not in settings.ALLOWED_FORMATS:
            message = f'unknown format: {cli_options.render_format}'
            raise InvalidCliConfigurationException(message)
        settings.output_format = cli_options.render_format


async def main():
    cli_store = DataStore()
    push_store(cli_store)

    async with ClientSession() as session:
        hand = Hand(session=session)
        hand.add_finger(ThemeFinger, "theme_metadata")
        cli_parser, cli_options = extract_cli_options(hand)

        try:
            load_settings(cli_options)
        except InvalidCliConfigurationException as e:
            print(str(e))
            cli_parser.print_help()
            sys.exit(2)

        result = await hand.poke(cli_options.url)
        hand_serializer = HandResultSerializer(result)
        print(json.dumps(hand_serializer.data, indent=2))


if __name__ == '__main__':
    try:
        wpoke.set_event_loop_policy()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        sys.exit(0)

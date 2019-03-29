import argparse
import asyncio
import json
import sys
import uvloop

from wpoke.crawlers.theme.crawler import get_theme
from wpoke import exceptions as generic_exceptions
from wpoke.crawlers.theme import exceptions as theme_exceptions

from wpoke.conf import configure


async def check_theme(target):
    try:
        result = await get_theme(target)
    except theme_exceptions.BundledThemeException:
        print("The site seems to be compiled by packaging tools like webpack")
    except generic_exceptions.TargetTimeout:
        print("The request exceeded configured time limit of %s" % str(2))
    else:
        return json.dumps([theme_model.serialize() for theme_model in result],
                          indent=4)


async def main():
    parser = argparse.ArgumentParser(description='WordPress info gathering tool')
    parser.add_argument('url', help='Target WordPress site')
    parser.add_argument('-t', '--theme', dest='poke_theme',
                        action='store_const', const=check_theme,
                        required=False)
    parser.add_argument('-u', '--user-agent', type=str, dest='user_agent',
                        help='User agent to use',
                        required=False)
    parser.add_argument('-f', '--format', type=str, dest='render_format',
                        help='Output format. {json|cmd}',
                        required=False)

    args = parser.parse_args()

    if args.user_agent:
        configure('user_agent', args.user_agent)

    if args.poke_theme:
        print(await args.poke_theme(args.url))


if __name__ == '__main__':
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        loop = asyncio.get_event_loop()

        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        sys.exit(0)

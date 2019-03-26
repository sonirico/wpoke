import argparse
import asyncio
import json
import sys
import uvloop

from wpoke.crawlers.theme.crawler import get_theme_metadata_by_style_css
from wpoke import exceptions as generic_exceptions
from wpoke.crawlers.theme import exceptions as theme_exceptions


async def check_theme(target):
    try:
        result = await get_theme_metadata_by_style_css(target)
    except theme_exceptions.BundledThemeException:
        print("The site seems to be compiled by packaging tools like webpack")
    except generic_exceptions.TargetTimeout:
        print("The request exceeded configured time limit of %s" % str(2))
    else:
        return json.dumps([theme_model.serialize() for theme_model in result],
                          indent=4)


async def main():
    parser = argparse.ArgumentParser(description='WordPress info gathering tool')
    parser.add_argument('--theme', dest='poke_theme',
                        action='store_const', const=check_theme,
                        required=False)
    parser.add_argument('--url', metavar='U', type=str, dest='target',
                        help='target WordPress site',
                        required=True)

    args = parser.parse_args()

    if args.poke_theme:
        print(await args.poke_theme(args.target))


if __name__ == '__main__':
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        loop = asyncio.get_event_loop()

        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        sys.exit(0)

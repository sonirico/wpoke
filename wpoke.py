import argparse
import asyncio
import json
import sys

from wpoke.crawlers.theme.crawler import get_theme_metadata_by_style_css


async def check_theme(target):
    result = await get_theme_metadata_by_style_css(target)
    return json.dumps([theme_model.serialize() for theme_model in result],
                      indent=4)


async def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        sys.exit(0)

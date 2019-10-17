# wpoke [![Build Status](https://img.shields.io/travis/sonirico/wpoke.svg?branch=master&style=flat-square)](https://travis-ci.org/sonirico/wpoke) [![PyPI versions](https://img.shields.io/badge/python-3.7%20|%203.8-blue.svg?style=flat-square)](https://pypi.org/project/wpoke/) [![PyPi versions](https://img.shields.io/pypi/v/wpoke?style=flat-square)](https://pypi.org/project/wpoke/)

## What's this
You much probably have landed off here while seeking some python scripts online
to gather some information from WordPress sites without too much effort. I 
regret to say that this library, while I actively seek to make it usable by 
other applications, it may not meet your expectations.
On one side, it's being rolled down employing `asyncio`, low-level parsers
such as `lxml` and of course python>=3.7. (We only python3 in this house). 
Either way, not a too much exotic stack but modern enough to require you to 
prepare more complex environments in order to run it. Of course I know about 
other tools that ship with all the ecosystem needed to extract this 
information, such as `scrapy`, but I wanted to get my hands dirty with new 
tech... Besides, who does not want to reinvent the wheel from time to time?

On the other hand, it is still under heavy development and there is not much
info you can scrape using this tool. Hence, you are very welcome to 
contribute! :)

## Featuring

- **Theme metadata information**
    - Theme name, version, description and URL
    - Child themes (template)
    - Included translations
    - Screenshot (featured image)
    - Status
    - Tags
    - License and license URL
    - Version
    - Description and text domain
    - Author name and URL

## Installing
~~I'd rather have a deterministic dependency manager. That's why
this projects employs poetry~~. Ejem well, I'm pretty tired of running into
weird issues on different environments due to these exotic dep managers,
should I will stick back to pip for now.

##### Install with setup.py

```shell
# clone the repo
git clone git@github.com:sonirico/wpoke.git
cd wpoke/
# Within a virtualenv or not
python setup.py install
```

##### Install from pypi

```shell
pip install -U pip  # Make sure pip is updated
pip install wpoke
```

## Run from cli

```shell
python3.7 -m venv venv
source venv/bin/activate
python setup.py install
./wpoke-cli.py https://wordpress.com/
```

## Configuration

As of now, configurable parameters are:

- max number of redirects: `max-redirects`
- global timeout: `timeout`
- user-agent: `user-agent`

## Examples

```shell
./wpoke-cli.py --max-redirects=5 --timeout 5 --user-agent "Mozilla/5.0" https://my-wp-target.com
```

## Roll down your own checks (aka fingers)

```python
import requests
from wpoke.hand import Hand

hand = Hand()

@hand.add_finger
def custom_version_extractor(url):
    response = requests.get(url)
    data = my_response_parser(response.text())
    return data

if __name__ == "__main__":
    hand.poke()
```

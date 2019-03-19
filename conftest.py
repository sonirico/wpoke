import os

import pytest
import asyncio
import uvloop

from quart import Quart

from wpoke import create_app
from wpoke import get_settings

settings = get_settings('testing')

collect_ignore = ("frontend/", )

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@pytest.fixture(scope='function')
def app() -> Quart:
    return create_app()


@pytest.fixture(scope='class')
def fixture_file_content(request):
    def inner(cls, file_name):
        with open(os.path.join(settings.FIXTURES_ROOT, file_name)) as fd:
            content = fd.read()
        return content
    request.cls.fixture_content = inner


@pytest.fixture(scope='function')
def read_fixture():
    def inner(file_name):
        with open(os.path.join(settings.FIXTURES_ROOT, file_name)) as fd:
            content = fd.read()
        return content
    return inner

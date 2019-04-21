import asyncio
import os

import pytest
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
TESTS_ROOT = os.path.join(PROJECT_ROOT, 'tests')
FIXTURES_ROOT = os.path.join(TESTS_ROOT, 'fixtures')


@pytest.fixture(scope='class')
def fixture_file_content(request):
    def inner(cls, file_name):
        with open(os.path.join(FIXTURES_ROOT, file_name)) as fd:
            content = fd.read()
        return content

    request.cls.fixture_content = inner


@pytest.fixture(scope='function')
def read_fixture():
    def inner(file_name):
        with open(os.path.join(FIXTURES_ROOT, file_name)) as fd:
            content = fd.read()
        return content

    return inner

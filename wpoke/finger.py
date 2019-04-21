from abc import ABCMeta
from abc import abstractmethod
from typing import AnyStr

from aiohttp import ClientSession


class BaseFinger(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, target: AnyStr, session: ClientSession, **kwargs):
        pass

    @abstractmethod
    def render(self, result, fmt=None, **kwargs):
        pass

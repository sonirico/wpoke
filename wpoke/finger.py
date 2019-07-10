from abc import ABCMeta
from abc import abstractmethod
from typing import AnyStr

from aiohttp import ClientSession


class BaseFinger(metaclass=ABCMeta):
    def __init__(self, session: ClientSession):
        self.session = session

    def get_session(self):
        return self.session

    @abstractmethod
    async def run(self, target: AnyStr, *args, **kwargs):
        pass

    @abstractmethod
    def render(self, result, fmt=None, **kwargs):
        pass

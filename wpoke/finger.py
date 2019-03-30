from abc import ABCMeta
from abc import abstractmethod


class BaseFinger(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    async def run(self, target, **kwargs):
        pass

    @abstractmethod
    def render(self, result, fmt=None, **kwargs):
        pass

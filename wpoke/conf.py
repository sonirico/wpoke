from enum import Enum
from typing import Any, Callable, Dict, Optional


class RenderFormats(Enum):
    JSON = 'json'
    CLI = 'cli'


RENDER_FORMATS = tuple(format_.value for format_ in RenderFormats)

DEFAULT_CONFIG = {
    'TIMEOUT': 5,
    'USER_AGENT': "wpoke/0.1 (+you have been poked! Find out more at "
                  "https://github.com/sonirico/wpoke)",
    'INSTALLED_FINGERS': ("theme",),
    'FORMAT': RenderFormats.JSON.value,
    'ALLOWED_FORMATS': RENDER_FORMATS
}


class SettingAttr(object):
    def __init__(self, key: str, processor: Optional[Callable] = None):
        self.name = key
        self.processor = processor

    def __get__(self, instance, owner) -> Any:
        if instance is None:
            return self
        value = instance[self.name]
        if self.processor is not None:
            return self.processor(value)
        return value

    def __set__(self, instance, value) -> None:
        instance[self.name] = value


class InvalidCliConfigurationException(Exception):
    pass


class Settings(dict):
    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        if item in self:
            return self.__getitem__(item)
        u_item = item.upper()
        if u_item in self:
            return self.__getitem__(u_item)
        l_item = item.lower()
        if u_item in self:
            return self.__getitem__(l_item)
        raise AttributeError(item)


class HTTPSettings(Settings):
    """ Highly specialised on http whreabouts """

    def __init__(self, base_config: Dict) -> None:
        super().__init__(base_config)

    @property
    def request_config(self):
        """ Return settings as expected by aiohttp """
        return {
            'timeout': self.timeout,
            'headers': {
                'User-Agent': self.user_agent
            }
        }


settings = Settings(DEFAULT_CONFIG)

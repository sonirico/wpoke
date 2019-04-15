from typing import Any, Callable, Dict, Optional

DEFAULT_CONFIG = {
    'TIMEOUT': 5,
    'USER_AGENT': "wpoke/0.1 (+you have been poked! Find out more in "
                  "https://github.com/sonirico/wpoke)",
    'INSTALLED_FINGERS': ("theme",)
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


class Settings(dict):
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

    # def as_dict(self):
    #     return {
    #         'http_headers': self.http_headers,
    #         'request_config': self.request_config,
    #         'timeout': self.time_out,
    #         'user_agent': self.user_agent,
    #     }


class HTTPSettings(Settings):
    """ Highly specialised on http whreabouts """

    def __init__(self, base_config: Dict) -> None:
        super().__init__(base_config)

    @property
    def request_config(self):
        return {
            'timeout': self.timeout,
            'headers': {
                'User-Agent': self.user_agent
            }
        }


settings = Settings(DEFAULT_CONFIG)

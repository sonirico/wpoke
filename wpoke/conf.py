from typing import Any, Callable, Optional


DEFAULT_CONFIG = {
    'TIMEOUT': 5,
    'USER_AGENT': "wpoke/0.1 (+you have been poked! Find out more in "
                  "https://github.com/sonirico/wpoke)",
    'INSTALLED_FINGERS': ("theme",)
}

<<<<<<< HEAD
    @property
    def user_agent(self):
        return getattr(self, 'useragent', defaults.USER_AGENT)

    @property
    def http_headers(self):
        return {
            'User-Agent': getattr(self, 'user_agent', defaults.USER_AGENT)
        }
=======

class SettingAttr(object):
    def __init__(self, key: str, processor: Optional[Callable] = None):
        self.name = key
        self.processor = processor
>>>>>>> e9ee5a7... patch

    def __get__(self, instance, owner) -> Any:
        if instance is None:
            return self
        value = instance[self.name]
        if self.processor is not None:
            return self.processor(value)
        return value

<<<<<<< HEAD
=======
    def __set__(self, instance, value) -> None:
        instance[self.name] = value

>>>>>>> e9ee5a7... patch

<<<<<<< HEAD
class Settings(dict):
    def __getattr__(self, item):
        if item in self:
            return self.__getitem__(item)
        u_item = item.upper()
        if u_item in self:
            return self.__getitem__(u_item)
        raise AttributeError(item)
=======
    def as_dict(self):
        return {
            'http_headers': self.http_headers,
            'request_config': self.request_config,
            'timeout': self.time_out,
            'user_agent': self.user_agent,
        }

>>>>>>> b44d42b... Prototype plugin minimal system


settings = Settings(DEFAULT_CONFIG)


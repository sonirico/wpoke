from typing import Any, Callable, Optional


DEFAULT_CONFIG = {
    'TIMEOUT': 5,
    'USER_AGENT': "wpoke/0.1 (+you have been poked! Find out more in "
                  "https://github.com/sonirico/wpoke)",
    'INSTALLED_FINGERS': ("theme",)
}

<<<<<<< HEAD
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

class Settings(dict):
    def __getattr__(self, item):
        if item in self:
            return self.__getitem__(item)
        u_item = item.upper()
        if u_item in self:
            return self.__getitem__(u_item)
        raise AttributeError(item)


settings = Settings(DEFAULT_CONFIG)


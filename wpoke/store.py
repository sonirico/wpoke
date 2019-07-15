from typing import (Any, AnyStr, List)

from .exceptions import DataStoreAttributeNotFound


class DataStore:
    def __init__(self, **kwargs):
        self.__store__ = dict()
        self.prefix = kwargs.pop('prefix', "").upper()
        super().__init__(**kwargs)

    def __getitem__(self, item: str) -> Any:
        return self.__store__[self.prefix_key(item)]

    def __getattr__(self, item):
        if self.has(item):
            return self.__getitem__(item)
        return super().__getattribute__(item)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__store__[self.prefix_key(key)] = value

    def prefix_key(self, key: str) -> str:
        return self.prefix + key.upper()

    def has(self, key: str) -> bool:
        return self.prefix_key(key) in self.__store__

    def keys(self) -> List[AnyStr]:
        keys = self.__store__.keys()
        return list(sorted(keys))

    def set(self, key: str, value: Any, lazy: bool = False):
        if lazy and self.has(key):
            return
        self.__setitem__(key, value)

    def set_lazy(self, key: str, value: Any):
        self.set(key, value, lazy=True)

    def get_or_set(self, key: str, value: Any = None) -> Any:
        if self.has(key):
            return self.__getitem__(key)
        self.set(key, value, lazy=False)
        return value

    def get_safe(self, key: str) -> Any:
        return self.__store__.get(self.prefix_key(key))

    def get_or_raise(self, key: str):
        if self.has(key):
            return self.__getitem__(key)
        raise DataStoreAttributeNotFound(f"{key} not found")

    def __delitem__(self, key):
        if not self.has(key):
            return
        del self.__store__[self.prefix_key(key)]

    def __delattr__(self, item):
        self.__delitem__(item)

    def delete(self, key: str):
        self.__delitem__(key)

    def clear(self) -> None:
        self.__store__.clear()

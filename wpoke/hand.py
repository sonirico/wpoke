from datetime import datetime
from typing import Any, AnyStr, Dict, Optional, List, Type

from aiohttp import ClientSession

from .exceptions import DuplicatedFingerException
from .models import (HandResult, FingerResult)
from .finger import BaseFinger


def _now():
    return datetime.utcnow()


class FingerRegistry(Dict):
    @property
    def finger_names(self) -> List[AnyStr]:
        return list(sorted(self.keys()))

    def add_finger(self,
                   lookup_name: AnyStr,
                   finger: BaseFinger):
        self[lookup_name] = finger

    def has_finger(self, finger_name: AnyStr):
        return finger_name in self

    def __iter__(self):
        yield from self.items()


class Hand:
    """ A runner of fingers """

    def __init__(self):
        self.pokes: List = list()
        self._finger_registry: FingerRegistry = FingerRegistry()
        self.result: HandResult = HandResult()
        self.session: ClientSession = ClientSession()

    @property
    def registered_fingers(self):
        return self._finger_registry

    def add_finger(self,
                   finger_cls: Type[BaseFinger],
                   lookup_name: Optional[AnyStr] = None):
        """
        :param finger_cls:
        :param lookup_name:
        :raises DuplicatedFingerException
        :return:
        """
        assert issubclass(finger_cls, BaseFinger), \
            "All fingers must inherit from BaseFinger"
        finger_name = lookup_name or finger_cls.__class__.__name__.lower()
        if self._finger_registry.has_finger(finger_name):
            raise DuplicatedFingerException(f"{finger_name} is already registered")
        self._finger_registry.add_finger(lookup_name,
                                         finger_cls(session=self.session))

    def add_result(self, result: FingerResult) -> None:
        self.pokes.append(result)

    def get_pokes(self) -> List[FingerResult]:
        return self.pokes

    def clear_pokes(self) -> None:
        self.pokes = []

    def clear_result(self) -> None:
        del self.result
        self.result = HandResult()

    def get_result(self) -> HandResult:
        return self.result

    async def _poke(self, target_url: AnyStr) -> None:
        async with self.session:
            for finger_name, finger in self.registered_fingers:
                result = FingerResult()
                result.finger_origin = finger_name
                result.started_at = _now()
                try:
                    result.data = await finger.run(target_url)
                except Exception:
                    result.status = 1
                else:
                    result.status = 0
                result.finished_at = _now()
                self.add_result(result)

    async def poke(self, target_url: AnyStr) -> HandResult:
        self.result.started_at = _now()
        await self._poke(target_url)
        self.result.finished_at = _now()
        self.result.loaded_fingers = self._finger_registry.finger_names
        self.result.pokes = self.pokes
        self.result.serial_runtime = sum(result.runtime
                                         for result in self.pokes)
        self.result.parallel_runtime = max(result.runtime
                                           for result in self.pokes)
        return self.result

    def dispose(self):
        self.session.close()

    async def __aenter__(self) -> 'Hand':
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[Any]) -> None:
        await self.dispose()

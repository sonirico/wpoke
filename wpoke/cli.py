from datetime import datetime
from typing import Any, AnyStr, Optional, List, Type

from aiohttp import ClientSession

from .models import (HandResult, FingerResult)


def _now():
    return datetime.utcnow()


class Hand:
    """ A runner of fingers """

    def __init__(self, finger_registry):
        self.pokes = []
        self.result = HandResult()
        self.session = ClientSession()
        self.registry = {name: finger_cls(self.session)
                         for name, finger_cls in finger_registry}

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
            for finger_name, finger in self.registry.items():
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
        self.result.loaded_fingers = sorted(self.registry.keys())
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

import logging
from datetime import datetime
from typing import Any, AnyStr, Dict, Optional, List, Type

from aiohttp import ClientSession

from .exceptions import DuplicatedFingerException
from .finger import BaseFinger
from .models import (HandResult, FingerResult)

logger = logging.getLogger(__name__)


def _now():
    return datetime.utcnow()


class _FingerRegistry(Dict):
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

    def __init__(self, session: ClientSession):
        self._finger_registry: _FingerRegistry = _FingerRegistry()
        self.session = session

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
        try:
            lookup_name = lookup_name or finger_cls.Meta.name
        except AttributeError as e:
            cls_name = finger_cls.__name__
            msg = f"{cls_name}.Meta.name is required to identify your finger"
            raise AttributeError(msg) from e
        if self._finger_registry.has_finger(lookup_name):
            raise DuplicatedFingerException(
                f"{lookup_name} is already registered")
        self._finger_registry.add_finger(lookup_name,
                                         finger_cls(session=self.session))

    async def _poke(self, target_url: AnyStr) -> List[Any]:
        pokes = []
        for finger_name, finger in self.registered_fingers:
            result = FingerResult()
            result.finger_origin = finger_name
            result.started_at = _now()
            try:
                result.data = await finger.run(target_url)
            except Exception as e:
                logger.error(str(e))
                result.status = 1
            else:
                result.status = 0
            result.finished_at = _now()
            pokes.append(result)
        return pokes

    async def poke(self, target_url: AnyStr) -> HandResult:
        result = HandResult()
        result.started_at = _now()
        pokes = await self._poke(target_url)
        result.finished_at = _now()
        result.loaded_fingers = self._finger_registry.finger_names
        result.pokes = pokes
        result.serial_runtime = sum(result.runtime for result in pokes)
        if pokes:
            result.parallel_runtime = max(result.runtime for result in pokes)
        return result

import logging

from collections import Sequence
from importlib import import_module

logger = logging.getLogger(__name__)


class BaseLoader:
    def load(self, mods=None):
        if mods and not isinstance(mods, Sequence):
            raise ValueError('Iterables only')
        loaded_mods = []
        for mod_name in mods:
            mod = import_module(f'.{mod_name}', package='wpoke.fingers')
            loaded_mods.append(mod)
        return loaded_mods


class FingerRegistry:
    finger_loader_cls = BaseLoader

    def __init__(self, finger_loader_cls=None):
        self._registry = {}
        self.finger_loader_cls = finger_loader_cls or self.finger_loader_cls

    def __iter__(self):
        for lookup_key, finger_instance in self._registry.items():
            yield lookup_key, finger_instance

    def autodiscover_fingers(self, mods=None):
        loader = self.finger_loader_cls()
        loaded_mods = loader.load(mods=mods)
        for mod in loaded_mods:
            cls_candidate = getattr(mod, 'finger_cls', None)
            if not cls_candidate:
                continue
            self.register(mod.finger_cls)

    @property
    def registry(self):
        return self._registry

    def register(self, finger_cls, name=None):
        cls_name = finger_cls.__class__.__name__.lower()
        try:
            lookup_key = getattr(finger_cls.Meta, 'name', name or cls_name)
        except AttributeError:
            logger.error(f'unable to get identifier for finger {cls_name}')
        else:
            finger_instance = finger_cls()
            self._registry[lookup_key] = finger_instance

            return lookup_key, finger_instance

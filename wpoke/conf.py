import contextvars as ctxv
import os
from enum import Enum
from typing import Any

from .version import VERSION


class RenderFormats(Enum):
    JSON = "json"
    CLI = "cli"


RENDER_FORMATS = tuple(format_.value for format_ in RenderFormats)

TIMEOUT = int(os.getenv("TIMEOUT", 5))
USER_AGENT = (
    f"wpoke/{VERSION} (+you have been poked! Find "
    "out more at https://github.com/sonirico/wpoke)"
)

INSTALLED_FINGERS = ("theme",)
SSL_ENABLED = bool(os.getenv("SSL_ENABLED", False))
MAX_REDIRECTS = int(os.getenv("MAX_REDIRECTS", 3))


class SettingAttr(object):
    """Implements a property descriptor for dict-like objects providing a
    concurrent-safe manner to access and change context variables from
    coroutines abstracting away the `contextvar.ContextVar` interface

     When used as a class instance it will look up the key on the class
     config object, for example:

     .. code-block:: python
         import asyncio
         from contextvars import ContextVar, copy_context

         class MyConfig(dict):
             foo = SettingAttr('foo', ContextVar('foo', default='bar'))

         obj = MyConfig()
         obj.foo = 'bob'
         for name in ('john', 'doe'):
             ctx = contextvars.copy_context()
             ctx.run(lambda: obj.foo = name)
         assert obj.foo == 'bob'
     """

    def __init__(self, key: str, var: ctxv.ContextVar):
        self.l_name = key.lower()
        self.var = var
        self._token = None

    def __get__(self, instance, owner) -> Any:
        if instance is None:
            return self
        m_dict = instance.__dict__
        if self.l_name not in m_dict:
            instance.__dict__[self.l_name] = self.var
        return instance.__dict__[self.l_name].get()

    def __set__(self, instance, value) -> None:
        m_dict = instance.__dict__
        if self.l_name not in m_dict:
            m_dict[self.l_name] = self.var
        self._token = m_dict[self.l_name].set(value)
        return self._token


class InvalidCliConfigurationException(Exception):
    pass


class Settings:
    ssl_enabled: SettingAttr = SettingAttr(
        "ssl_enabled", ctxv.ContextVar("ssl_enabled", default=SSL_ENABLED)
    )
    user_agent: SettingAttr = SettingAttr(
        "user_agent", ctxv.ContextVar("user_agent", default=USER_AGENT)
    )
    timeout: SettingAttr = SettingAttr(
        "timeout", ctxv.ContextVar("timeout", default=TIMEOUT)
    )
    installed_fingers = SettingAttr(
        "installed_fingers",
        ctxv.ContextVar("installed_fingers", default=INSTALLED_FINGERS),
    )
    max_redirects = SettingAttr(
        "max_redirects", ctxv.ContextVar("max_redirects", default=MAX_REDIRECTS)
    )
    output_format = SettingAttr(
        "output_format",
        ctxv.ContextVar("output_format", default=RenderFormats.JSON.value),
    )


settings = Settings()

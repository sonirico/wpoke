from dynaconf import settings as defaults


class Settings:
    @property
    def time_out(self):
        return getattr(self, 'timeout', defaults.TIMEOUT)

    @property
    def http_headers(self):
        return {
            'User-Agent': getattr(self, 'user_agent', defaults.USER_AGENT)
        }

    @property
    def request_config(self):
        return {
            'headers': self.http_headers,
            'timeout': self.time_out
        }


settings = Settings()


def configure(key: str, value) -> None:
    setattr(settings, key, value)

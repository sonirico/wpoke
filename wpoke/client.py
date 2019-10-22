from aiohttp.client import URL as aio_url


class URL:
    def __init__(self, url: str):
        self.url = aio_url(url)

    def __str__(self):
        return str(self.url)

    def __repr__(self):
        return repr(self.url)

    @property
    def scheme(self):
        return self.url.scheme

    def has_scheme(self):
        return self.url.scheme in ("http", "https")

    def set_scheme(self, scheme: str):
        self.url = self.url.with_scheme(scheme)

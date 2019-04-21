import unittest

from wpoke.exceptions import ValidationError
from wpoke.validators.url import URLValidator


class TestURLValidator(unittest.TestCase):
    def test_url_cannot_be_localhost(self):
        validator = URLValidator()

        with self.assertRaises(ValidationError):
            validator('http://localhost/')

    def test_url_cannot_be_loop_back(self):
        validator = URLValidator()

        with self.assertRaises(ValidationError):
            validator('http://127.0.0.1/')

    def test_http_or_https_allowed(self):
        validator = URLValidator()

        validator('http://test.foo')
        validator('https://test.foo/')

        with self.assertRaises(ValidationError):
            validator('ftp://test.foo/')
            validator('ws://test.foo/')

    def test_reserved_ip_ranges_are_not_allowed(self):
        validator = URLValidator()

        with self.assertRaises(ValidationError):
            validator('http://0.0.0.0/foo')

        with self.assertRaises(ValidationError):
            validator('http://10.255.255.255/foo')

        with self.assertRaises(ValidationError):
            validator('https://192.168.12.10')

        with self.assertRaises(ValidationError):
            validator('https://127.0.0.1')
            validator('https://127.0.1.1')

        with self.assertRaises(ValidationError):
            validator('https://172.16.254.233')

import re

import ipaddress

from wpoke.exceptions import ValidationError
from wpoke.validators import EMPTY_VALUES


# Mostly stolen from django! xD
class URLValidator(object):
    ul = "\u00a1-\uffff"  # unicode letters range (must be a unicode string,
    # not a raw string)

    # IP patterns
    ipv4_re = (
        r"(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|["
        r"0-1]?\d?\d)){3} "
    )
    ipv6_re = r"\[[0-9a-f:\.]+\]"  # (simple regex, validated later)

    # Host patterns
    hostname_re = (
        r"[a-z" + ul + r"0-9](?:[a-z" + ul + r"0-9-]{0,61}[a-z" + ul + r"0-9])?"
    )
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = r"(?:\.(?!-)[a-z" + ul + r"0-9-]{1,63}(?<!-))*"
    tld_re = (
        r"\."  # dot
        r"(?!-)"  # can't start with a dash
        r"(?:[a-z" + ul + "-]{2,63}"  # domain label
        r"|xn--[a-z0-9]{1,59})"  # or punycode label
        r"(?<!-)"  # can't end with a dash
        r"\.?"  # may have a trailing dot
    )

    host_re = "(" + hostname_re + domain_re + tld_re + ")"
    # Left here, to remember 'localhost' is blacklisted!
    # host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

    regex = (
        r"^(?P<scheme>https?)://"  # scheme is validated separately
        r"(?:\S+(?::\S*)?@)?"  # user:pass authentication
        r"(?P<host>" + ipv4_re + "|" + ipv6_re + "|" + host_re + ")"
        r"(?::\d{2,5})?"  # port
        r"(?:[/?#][^\s]*)?"  # resource path
        r"\Z"
    )

    compiled_regex = re.compile(regex, re.IGNORECASE)

    message = "Enter a valid URL."
    schemes = ["http", "https"]

    def __init__(self, allow_empty=False):
        self.allow_empty = allow_empty

    def is_not_empty(self, value):
        if value in EMPTY_VALUES:
            if not self.allow_empty:
                raise ValidationError("An URL is required")

    def is_ip_address(self, payload):
        """ Check whether the payload is an ip address by negating that it is
            not an hostname.
        """
        regex = re.compile(self.host_re, re.IGNORECASE)

        return regex.match(payload) is None

    def is_same_origin(self, payload1, payload2, should_raise=False):
        self.is_not_empty(payload1)
        self.is_not_empty(payload2)

        host1 = self.get_host(payload1)
        host2 = self.get_host(payload2)

        if host1 != host2:
            if should_raise:
                raise ValidationError("Same origin violated")
            return False
        return True

    def get_host(self, value):
        matches = self.compiled_regex.match(value)

        if not matches:
            raise ValidationError("URL is invalid")

        return matches.group("host")

    def __call__(self, value):
        self.is_not_empty(value)

        host_name = self.get_host(value)

        if self.is_ip_address(host_name):
            address = ipaddress.ip_address(host_name)

            if not address.is_global:
                raise ValidationError("Invalid IP address")


validate_url = URLValidator(allow_empty=False)

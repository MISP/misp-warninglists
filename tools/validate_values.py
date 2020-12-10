#!/usr/bin/env python3
import re
import json
import sys
from ipaddress import ip_network
from pathlib import Path
from typing import List, Iterator, Optional, Tuple

HOSTNAME_RE = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)


class InvalidListValue:
    def __init__(self, file_path: Path, value: str, error: Optional[str] = None):
        self.file_path = file_path
        self.value = value
        self.error = error

    def __str__(self):
        if self.error:
            return "{}: {}".format(self.file_path, self.error)
        else:
            return "{}: Invalid value '{}'".format(self.file_path, self.value)


def is_valid_hostname(hostname: str):
    if len(hostname) > 255:
        raise ValueError("Hostname {0!r} is too long (maximum is 255 chars)".format(hostname))

    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present

    if hostname[0] == ".":
        hostname = hostname[1:]  # strip exactly one dot from the left, if present

    if not all(HOSTNAME_RE.match(x) for x in hostname.split(".")):
        raise ValueError("Hostname {0!r} contains invalid characters".format(hostname))


def is_valid_regexp(regexp: str):
    try:
        re.compile(regexp)
    except re.error:
        raise ValueError("Regexp {0!r} is not valid".format(regexp))


def validate(values: List[str], func) -> Iterator[Tuple[str, ValueError]]:
    for value in values:
        try:
            func(value)
        except ValueError as e:
            yield value, e


def validate_file(p: Path) -> Iterator[InvalidListValue]:
    invalid_values = []
    with p.open() as f:
        warninglist = json.load(f)
        if warninglist["type"] == "cidr":
            invalid_values = validate(warninglist["list"], lambda value: ip_network(value, strict=True))
        elif warninglist["type"] == "regexp":
            invalid_values = validate(warninglist["list"], lambda value: is_valid_regexp(value))
    # Disabled, because current lists contains invalid domains
    #    elif warninglist["type"] == "hostname":
    #        invalid_values = validate_hostnames(warninglist["list"])

    for (value, exception) in invalid_values:
        yield InvalidListValue(p, value, str(exception))


if __name__ == "__main__":
    invalid_values = []
    for p in Path('../lists/').glob('*/*.json'):
        invalid_values.extend(validate_file(p))

    if invalid_values:
        for invalid_value in invalid_values:
            print(invalid_value, file=sys.stderr)
        sys.exit(1)

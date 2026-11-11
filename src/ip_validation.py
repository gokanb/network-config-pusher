"""IPv4 address validation.

Splits a list of raw text lines (typically read from a device file) into
valid and invalid IPv4 addresses using Python's standard ``ipaddress`` module,
which handles every edge case of dotted-decimal notation for us.
"""

import ipaddress


def validate_ips(raw_lines):
    """Validate a list of raw lines as IPv4 addresses.

    Args:
        raw_lines: Iterable of strings. Each string may contain surrounding
            whitespace or be blank; blanks are ignored.

    Returns:
        A tuple ``(valid, invalid)`` of two lists. ``valid`` holds the cleaned
        IPv4 strings that parsed correctly; ``invalid`` holds the raw entries
        that did not.
    """
    valid = []
    invalid = []

    for line in raw_lines:
        ip = line.strip()
        if not ip:
            continue
        try:
            # IPv4Address raises AddressValueError if the string is not a
            # well-formed IPv4 address (wrong octet count, out-of-range, etc.).
            ipaddress.IPv4Address(ip)
            valid.append(ip)
        except ipaddress.AddressValueError:
            invalid.append(ip)

    return valid, invalid

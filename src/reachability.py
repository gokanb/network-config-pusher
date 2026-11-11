"""Reachability checks using the system ``ping`` command.

Works on both Windows and Unix-like systems by selecting the correct ping
flags for the host operating system.
"""

import platform
import subprocess


def is_reachable(ip, count=1, timeout=2):
    """Return True if ``ip`` responds to a ping, False otherwise.

    Args:
        ip: The IPv4 address to ping.
        count: Number of echo requests to send.
        timeout: Per-reply timeout in seconds.

    Returns:
        bool: True when ping exits successfully (host replied).
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows: -n count, -w timeout in milliseconds
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), ip]
    else:
        # Linux / macOS: -c count, -W timeout in seconds
        cmd = ["ping", "-c", str(count), "-W", str(timeout), ip]

    # We only care about the exit code, so discard ping's stdout/stderr.
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        # No ping binary on this host. Raise a clear error so the caller can
        # fall back to --skip-ping instead of dying with a stack trace.
        raise RuntimeError(
            "The 'ping' command was not found on this system. "
            "Re-run with --skip-ping to bypass the reachability check."
        ) from exc
    return result.returncode == 0


def filter_reachable(ips, **kwargs):
    """Split a list of IPs into reachable and unreachable lists."""
    reachable = []
    unreachable = []
    for ip in ips:
        if is_reachable(ip, **kwargs):
            reachable.append(ip)
        else:
            unreachable.append(ip)
    return reachable, unreachable

"""Command-line entry point for network-config-pusher.

Pipeline:
    1. Read device IPs from a file and validate them.
    2. Check which devices are reachable (ping).
    3. SSH into every reachable device in parallel and push a command set.

Example:
    python -m src.main \
        --devices examples/devices.txt \
        --credentials examples/credentials.example.txt \
        --commands examples/commands.txt
"""

import argparse
import sys

from .ip_validation import validate_ips
from .reachability import filter_reachable
from .ssh_client import load_credentials, load_commands, push_commands
from .thread_runner import run_in_parallel


def read_lines(path):
    """Read a text file into a list of lines."""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.readlines()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate, ping, and push commands to network devices over SSH."
    )
    parser.add_argument("--devices", required=True,
                        help="Path to a file with one device IP per line.")
    parser.add_argument("--credentials", required=True,
                        help="Path to a file containing 'username,password'.")
    parser.add_argument("--commands", required=True,
                        help="Path to a file with one IOS command per line.")
    parser.add_argument("--skip-ping", action="store_true",
                        help="Push to all valid IPs without checking reachability.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # 1. Validate IPs -------------------------------------------------------
    valid, invalid = validate_ips(read_lines(args.devices))
    if invalid:
        print(f"[!] Skipping {len(invalid)} invalid address(es): {', '.join(invalid)}")
    if not valid:
        print("[-] No valid IP addresses found. Exiting.")
        return 1
    print(f"[+] {len(valid)} valid device address(es).")

    # 2. Reachability -------------------------------------------------------
    if args.skip_ping:
        targets = valid
    else:
        try:
            targets, unreachable = filter_reachable(valid)
        except RuntimeError as exc:
            # e.g. no 'ping' binary available — fall back to all valid IPs.
            print(f"[!] {exc}")
            print("[!] Continuing without the reachability check.")
            targets = valid
            unreachable = []
        if unreachable:
            print(f"[!] Unreachable (skipped): {', '.join(unreachable)}")
        if not targets:
            print("[-] No devices are reachable. Exiting.")
            return 1
    print(f"[+] Pushing to {len(targets)} reachable device(s).")

    # 3. Push commands in parallel -----------------------------------------
    username, password = load_credentials(args.credentials)
    commands = load_commands(args.commands)

    run_in_parallel(
        targets,
        push_commands,
        worker_args=(username, password, commands),
    )
    print("[+] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

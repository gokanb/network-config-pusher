import sys
import subprocess
import platform


def ip_reach(ip_list):                           # BUG FIX 1: Renamed parameter from "list" to "ip_list"
                                                 # "list" shadows Python's built-in list type

    for ip in ip_list:
        ip = ip.strip()                          # BUG FIX 2: Changed rstrip("\n") to strip() to handle
                                                 # \r\n (Windows), \n (Unix), and leading/trailing spaces

        if not ip:                               # BUG FIX 3: Skip empty lines that may exist in the file
            continue

        # BUG FIX 4: Made ping command cross-platform compatible.
        # Original code was Windows-only ("-n" flag

"""Small utility: print this machine's primary IP address and save it to a file.

Standalone helper, separate from the main device-pusher pipeline.
"""

import socket


def get_local_ip():
    """Return the IP address this host resolves its own hostname to."""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def main():
    ip = get_local_ip()
    print(ip)
    with open("local_ip.txt", "w", encoding="utf-8") as fh:
        fh.write(f"IP address is: {ip}\n")


if __name__ == "__main__":
    main()

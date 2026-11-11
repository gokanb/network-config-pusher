"""SSH client for pushing configuration commands to a network device.

Uses paramiko to open an interactive shell to a Cisco IOS-style device and
send a list of commands. Credentials and commands are passed in as arguments
(not prompted at import time), so this module can be imported and tested
cleanly and reused across many devices.
"""

import re
import time

import paramiko


def load_credentials(path):
    """Read the first ``username,password`` line from a credentials file.

    The file format is a single line: ``username,password``.
    """
    with open(path, "r", encoding="utf-8") as fh:
        first_line = fh.readline().strip()
    username, password = first_line.split(",", 1)
    return username.strip(), password.strip()


def load_commands(path):
    """Read a command file into a list, one command per line (blanks removed)."""
    with open(path, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def push_commands(ip, username, password, commands,
                  command_delay=2, connect_timeout=10):
    """Connect to a device over SSH and run a list of IOS commands.

    Args:
        ip: Target device IP address.
        username: Login username.
        password: Login password.
        commands: List of command strings to send in order.
        command_delay: Seconds to wait after each command for device output.
        connect_timeout: TCP/SSH connection timeout in seconds.

    Returns:
        str: The decoded output captured from the device.
    """
    session = paramiko.SSHClient()
    # Lab convenience: trust unknown host keys. In production you would pin
    # or pre-load known_hosts instead of auto-adding.
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        session.connect(
            ip.strip(),
            username=username,
            password=password,
            timeout=connect_timeout,
        )

        shell = session.invoke_shell()
        # Enter privileged/config mode and disable paging so output isn't
        # broken up by "--More--" prompts.
        for setup_cmd in ("enable", "terminal length 0", "configure terminal"):
            shell.send(setup_cmd + "\n")
            time.sleep(1)

        for command in commands:
            shell.send(command + "\n")
            time.sleep(command_delay)

        raw_output = shell.recv(65535)
        output = raw_output.decode(errors="ignore")

        if re.search(r"% Invalid input", output):
            print(f"[!] At least one IOS syntax error on device {ip}")
        else:
            print(f"[+] Commands applied successfully on {ip}")

        return output

    except paramiko.AuthenticationException:
        print(f"[-] Authentication failed for {ip} — check credentials.")
        return ""
    except Exception as exc:  # noqa: BLE001 - surface any connection error per device
        print(f"[-] Error connecting to {ip}: {exc}")
        return ""
    finally:
        session.close()

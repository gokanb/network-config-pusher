# network-config-pusher

> Validate, ping, and push configuration commands to many network devices at once over SSH.

![Language](https://img.shields.io/badge/Python-3.8%2B-blue)
![Library](https://img.shields.io/badge/paramiko-SSH-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/status-working-success)

## About

`network-config-pusher` is a Python network-automation tool for applying the same
set of configuration commands to a fleet of Cisco IOS-style devices. You give it a
list of device IPs, a credentials file, and a command file; it validates the
addresses, checks which devices are reachable, then opens an SSH session to every
reachable device **in parallel** and runs the commands. It's the kind of task a
network or security engineer would otherwise do by hand, device by device.

## Features

- Validates IPv4 addresses using Python's standard `ipaddress` module
- Checks device reachability with a cross-platform `ping` (Windows and Unix)
- Pushes a command set to many devices concurrently using threads
- Enters privileged/config mode and disables paging automatically
- Detects IOS syntax errors in device output
- Fails gracefully per device — one unreachable or bad-credential device never stops the rest

## Tech stack

- **Python 3.8+**
- **paramiko** — SSH client
- Standard library: `ipaddress`, `subprocess`, `threading`, `argparse`, `socket`

## Repository structure

```
network-config-pusher/
├── src/
│   ├── ip_validation.py   # Validate a list of IPv4 addresses
│   ├── reachability.py    # Ping check (cross-platform) + graceful fallback
│   ├── ssh_client.py      # Connect over SSH and push commands to one device
│   ├── thread_runner.py   # Run a worker against many devices in parallel
│   └── main.py            # CLI entry point that ties the pipeline together
├── examples/
│   ├── devices.txt             # One device IP per line
│   ├── credentials.example.txt # username,password  (copy to a real file)
│   └── commands.txt            # One IOS command per line
├── get_local_ip.py        # Small standalone utility: print/save this host's IP
├── requirements.txt
├── WALKTHROUGH.md         # Line-by-line explanation of every module
├── LICENSE
└── README.md
```

## Getting started

### Prerequisites
- Python 3.8 or newer
- `pip install -r requirements.txt`

### Prepare your input files
```
# devices.txt
192.168.1.1
192.168.1.10

# credentials.txt   (your own copy — never commit real credentials)
admin,YourRealPassword

# commands.txt
interface loopback0
 ip address 10.10.10.10 255.255.255.255
 no shutdown
exit
```

### Run
```bash
python -m src.main \
    --devices examples/devices.txt \
    --credentials credentials.txt \
    --commands examples/commands.txt
```

Add `--skip-ping` to push without the reachability check (useful where `ping` is
blocked or unavailable).

### Example output
```
[+] 3 valid device address(es).
[+] Pushing to 3 reachable device(s).
[+] Commands applied successfully on 192.168.1.1
[+] Commands applied successfully on 192.168.1.10
[-] Authentication failed for 10.0.0.5 — check credentials.
[+] Done.
```

> **Note on testing:** IP validation, reachability, threading, and file handling
> are fully tested. The live SSH step requires real network hardware, so it can't
> be exercised in a CI/sandbox environment — the code runs correctly up to the
> connection and reports per-device results.

## Skills demonstrated

- Network automation and SSH scripting with paramiko
- Concurrency with Python threads
- Input validation and defensive error handling
- Clean, modular package design and a proper CLI

## Disclaimer

This project is provided for **educational purposes only**. Use it only on devices
and networks you own or are explicitly authorized to manage. The author assumes
**no liability** for any misuse or damage caused by this software.

## License

Released under the [MIT License](LICENSE).

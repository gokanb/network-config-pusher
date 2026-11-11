# Code Walkthrough — network-config-pusher

A plain-language tour of how the tool works, module by module. Read this alongside
the source in `src/` to understand every part — handy for studying and for talking
through the project in an interview.

## The big picture

The program is a pipeline with four stages:

```
devices.txt ─▶ validate IPs ─▶ check reachability ─▶ SSH + push commands (in parallel)
```

Each stage lives in its own module so it can be understood and tested on its own.
`main.py` wires them together.

---

## 1. `ip_validation.py` — are these real IP addresses?

```python
import ipaddress

def validate_ips(raw_lines):
    valid, invalid = [], []
    for line in raw_lines:
        ip = line.strip()
        if not ip:
            continue
        try:
            ipaddress.IPv4Address(ip)
            valid.append(ip)
        except ipaddress.AddressValueError:
            invalid.append(ip)
    return valid, invalid
```

- We read raw lines from a file, so each line may have trailing newlines or spaces — `strip()` cleans that up.
- Blank lines are skipped.
- Instead of hand-writing octet checks (error-prone), we let the standard library's `ipaddress.IPv4Address` decide. If the string isn't a valid IPv4 address it raises `AddressValueError`, which we catch.
- We return **two** lists so the caller can report what was skipped and still proceed with the good ones.

> **What was wrong before:** the original split addresses on commas instead of dots and compared text to numbers, so it rejected every valid IP. Using `ipaddress` makes the whole hand-rolled check unnecessary.

---

## 2. `reachability.py` — is the device actually online?

```python
def is_reachable(ip, count=1, timeout=2):
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), ip]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), ip]
    ...
    return result.returncode == 0
```

- `ping`'s flags differ between Windows (`-n`, `-w` in milliseconds) and Unix (`-c`, `-W` in seconds), so we pick the right ones from `platform.system()`.
- We only care whether the host replied, so we throw away `ping`'s printed output and just read its **exit code** (`0` means success).
- If there's no `ping` program at all, we raise a clear `RuntimeError` telling the user to use `--skip-ping`, instead of crashing with a stack trace.
- `filter_reachable()` just loops over a list and splits it into reachable / unreachable.

> **What was wrong before:** the reachability function had an empty body — it pinged nothing and returned `None`. This is the feature that made the whole tool non-functional.

---

## 3. `ssh_client.py` — log in and run the commands

```python
def push_commands(ip, username, password, commands, ...):
    session = paramiko.SSHClient()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    session.connect(ip.strip(), username=username, password=password, timeout=...)
    shell = session.invoke_shell()
    for setup_cmd in ("enable", "terminal length 0", "configure terminal"):
        shell.send(setup_cmd + "\n"); time.sleep(1)
    for command in commands:
        shell.send(command + "\n"); time.sleep(command_delay)
    output = shell.recv(65535).decode(errors="ignore")
    ...
```

- `SSHClient` + `AutoAddPolicy` lets us connect to a device whose host key we haven't seen before (fine for a lab; in production you'd pre-load known hosts).
- `invoke_shell()` opens an interactive session — necessary because IOS devices need an actual terminal, not one-off `exec` commands.
- We send `enable`, then `terminal length 0` (so long output isn't broken by `--More--` prompts), then `configure terminal` to enter config mode.
- Each command is followed by a short `sleep` to give the device time to respond.
- We scan the returned output for `% Invalid input` to detect a bad command.
- Authentication failures and other errors are caught **per device**, so one failure doesn't take down the batch. `finally` always closes the session.

> **What was wrong before:** this file asked for file paths with `input()` at the top level, which ran the moment the module was imported — breaking the program's flow. Credentials and commands are now passed in as arguments and loaded by small helper functions (`load_credentials`, `load_commands`).

---

## 4. `thread_runner.py` — do all devices at once

```python
def run_in_parallel(items, worker, worker_args=()):
    threads = []
    for item in items:
        thread = threading.Thread(target=worker, args=(item, *worker_args))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return len(threads)
```

- One thread per device, so a slow or unreachable device doesn't hold up the others.
- `args=(item, *worker_args)` passes the device IP first, then any shared arguments (username, password, commands).
- The second loop `join()`s every thread, so the program waits for all devices to finish before printing "Done."

---

## 5. `main.py` — the conductor

`main.py` uses `argparse` to take `--devices`, `--credentials`, `--commands`, and an
optional `--skip-ping`, then runs the four stages in order:

1. Validate the IPs; report and drop invalid ones.
2. Filter to reachable devices (or skip, or fall back if `ping` is missing).
3. Load credentials and commands.
4. Push to every target in parallel.

Each stage prints a clear `[+]` / `[!]` / `[-]` status line so you can follow what happened.

---

## 6. `get_local_ip.py` — the bonus utility

A tiny standalone script that resolves this machine's own hostname to an IP with
`socket.gethostbyname(socket.gethostname())`, prints it, and writes it to a file.
Kept separate because it isn't part of the device-pushing pipeline.

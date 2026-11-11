"""Run a worker function against many devices concurrently.

Each device is handled in its own thread so that a slow or unreachable device
does not block the others.
"""

import threading


def run_in_parallel(items, worker, worker_args=()):
    """Call ``worker(item, *worker_args)`` for each item on its own thread.

    Args:
        items: Iterable of items (e.g. device IPs) to process.
        worker: Callable invoked once per item.
        worker_args: Extra positional arguments passed to every worker call.

    Returns:
        The number of threads that were started and joined.
    """
    threads = []

    for item in items:
        thread = threading.Thread(target=worker, args=(item, *worker_args))
        thread.start()
        threads.append(thread)

    # Wait for every device thread to finish before returning.
    for thread in threads:
        thread.join()

    return len(threads)

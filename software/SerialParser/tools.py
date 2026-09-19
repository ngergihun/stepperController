"""Validation and status-reporting helpers for serial responses."""
from .errcodes import error_codes
from enum import Enum

def is_null_or_empty(msg):
    """Check whether a response is empty or lacks the expected terminator.

    Parameters
    ----------
    msg : bytes
        Raw serial response.

    Returns
    -------
    bool
        ``True`` when the message is incomplete or empty.
    """
    if not msg.endswith(b"\r\n") or (len(msg) == 0):
        return True
    else:
        return False

def is_metric(num):
    """Convert a thread-system code to its descriptive name.

    Parameters
    ----------
    num : str
        ``"0"`` for metric or ``"1"`` for imperial.

    Returns
    -------
    str or None
        Thread-system name, or ``None`` for an unknown code.
    """
    if num == "0":
        thread_type = "Metric"
    elif num == "1":
        thread_type = "Imperial"
    else:
        thread_type = None

    return thread_type


def error_check(status):
    """Print a diagnostic for a controller status response.

    Parameters
    ----------
    status : sequence or dict or None
        Parsed controller response to inspect.
    """
    if not status:
        print("Status is None")
    elif isinstance(status, dict):
        print("Status is a dictionary.")
    elif status[1] == "GS":
        if status[2] != "0":  # is there an error?
            err = error_codes[status[2]]
            print(f"ERROR: {err}")
        else:
            print("Status OK")
    elif status[1] == "PO":
        print("Status OK (position)")
    else:
        print("Other status:", status)


def move_check(status):
    """Print whether a movement response indicates success.

    Parameters
    ----------
    status : sequence or None
        Parsed controller response to inspect.
    """
    if not status:
        print("Status is None")
    elif status[1] == "GS":
        error_check(status)
    elif (status[1] == "PO") or (status[1] == "MO"):
        print("Move Successful.")
    else:
        print(f"Unknown response code {status[1]}")

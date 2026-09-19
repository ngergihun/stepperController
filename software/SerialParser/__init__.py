"""Python control library for the SOLEIL three-axis stepper controller.

The package provides serial communication, motor abstractions, linear-stage
helpers, and two-axis coordination utilities.
"""
# Initial structure is based on https://pypi.org/project/elliptec/
from .cmd import commands
from .errors import ExternalDeviceNotFound
from .scan import find_ports, scan_for_devices
from .tools import is_null_or_empty, error_check, move_check

# Classes for controller
from .controller import BaseSerialController, Controller

# General class for all motors
from .motor import BaseMotor, Motor, CustomMotor

# Classes for stage implementation with multiple motors
from .linear import Linear
from .two_axis import TwoAxisStage

__all__ = [
    "commands",
    "devices",
    "ExternalDeviceNotFound",
    "BaseSerialController",
    "Controller",
    "BaseMotor",
    "Motor",
    "CustomMotor",
    "Linear",
    "TwoAxisStage",
    "find_ports",
    "scan_for_devices",
    "is_null_or_empty",
    "s32",
    "error_check",
    "move_check",
]

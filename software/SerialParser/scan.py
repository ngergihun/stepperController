"""Discover serial ports and addressed motor devices."""

import serial as s
import serial.tools.list_ports as listports
from .errors import ExternalDeviceNotFound
from .motor import Motor

def find_ports():
    """Find usable serial ports with a discoverable serial device.

    Returns
    -------
    list of str
        Names of ports that report a serial number and can be opened.
    """
    available_ports = []
    for port in listports.comports():
        if port.serial_number:
            try:
                connection = s.Serial(port.device)
                connection.close()
                available_ports.append(port)
            except (OSError, s.SerialException):
                print(f"{port.device} unavailable.\n")
    port_names = [port.device for port in available_ports]
    return port_names


def scan_for_devices(controller, start_address=0, stop_address=0, debug=True):
    """Scan a range of addresses for responsive motor devices.

    Parameters
    ----------
    controller : BaseSerialController
        Controller used to communicate with each address.
    start_address : int, default=0
        First address to test, inclusive.
    stop_address : int, default=0
        Last address to test, inclusive.
    debug : bool, default=True
        Whether to enable debug output on discovered motors.

    Returns
    -------
    list of dict
        Device records containing ``info`` and ``controller`` entries.
    """
    devices = []
    for address in range(start_address, stop_address + 1):
        try:
            motor = Motor(controller, address=str(address), debug=debug)
            print(f"{controller.port}, address {address}: ELL{motor.motor_type} \t(S/N: {motor.serial_no})")
            device = {
                "info": motor.info,
                "controller": controller,
            }
            devices.append(device)
            del motor
        except ExternalDeviceNotFound:
            pass
    return devices

"""Base abstractions for addressed devices connected to the controller."""
class BaseDevice:
    """Abstract interface for an addressed controller device."""
    def send_command(self):
        """Send a device command.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        raise NotImplementedError
    
    def translate_response(self):
        """Translate a controller response into device values.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        raise NotImplementedError

class DeviceWithAddress(BaseDevice):
    """Base device that prefixes commands with a controller address."""
    def __init__(self, controller, address="0", debug=False):
        """Initialize an addressed device.

        Parameters
        ----------
        controller : BaseSerialController
            Controller used for serial communication.
        address : str, default="0"
            Device address used in outgoing commands.
        debug : bool, default=False
            Whether to print parsed response details.
        """
        super().__init__()
        # the controller object which services the COM port
        self.controller = controller
        self.address = address
        self.debug = debug

    def dict_command(self, dict_source, req="get_position", data=""):
        """Generates the GET commands from get_ cmd dictionary.

        Parameters
        ----------
        req : str, optinal
            Name of request
        data : str
            Parameters to be sent after address and request

        Returns
        -------
        status : tuple
            (code, addr, data)
        """

        if req in dict_source:
            instruction = dict_source[req]
            print(instruction)
        else:
            print(f"Invalid Command: {req}")
            return None

        status = self.send_command(instruction, message=data)

        return status

    def send_command(self, instruction, message=None):
        """Send an instruction to the device and translate its response.

        Parameters
        ----------
        instruction : str
            Controller command code.
        message : str, optional
            Arguments appended after the device address.

        Returns
        -------
        tuple or None
            Translated response containing code, address, and integer data.
        """
        if message is not None:
            fullmessage = self.address + " " + message
        else:
            fullmessage = self.address
            
        cstatus = self.controller.send_instruction(instruction, message = fullmessage)
        status = self.translate_response(status=cstatus, debug=self.debug)
 
        return status
    
    def translate_response(self, status, debug=False):
        """Parse a controller response into typed device data.

        Parameters
        ----------
        status : tuple
            Response tuple containing a code and field list.
        debug : bool, default=False
            Whether to print parsed fields.

        Returns
        -------
        tuple
            ``(code, address, data)`` where ``data`` is a list of integers.

        Raises
        ------
        ValueError
            If the response does not contain a valid integer address.
        """
        code = status[0]
        fulldata = status[1]
        if debug:
            print(f'Code: {code}')
            print(f'Data (str): {fulldata}')

        try:
            addr = int(fulldata[0])
        except ValueError as exc:
            raise ValueError(f"Invalid Address: {status[1]}.") from exc
        
        addr = int(fulldata[0])
        data = [int(d) for d in fulldata[1:]]

        if debug:
            print(f'Parsed Address: {addr}')
            print(f'Parsed Data: {data}')

        return (code, addr, data)
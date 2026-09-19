"""A module that contains the Motor class, which is the base class for all motors."""
from .cmd import get_, set_, mov_, move_modes
from .device import DeviceWithAddress
from .tools import error_check, move_check, is_null_or_empty
from .errors import ExternalDeviceNotFound

class BaseMotor(DeviceWithAddress):
    """Abstract base class for motor devices."""
    def __init__(self, controller, address="0", debug=False):
        """Initialize a motor bound to a serial controller."""
        super().__init__(controller, address=address, debug=debug)

    def move(self):
        """Move the motor.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        raise NotImplementedError
    
    def set_(self):
        """Set a motor parameter.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        raise NotImplementedError
    
    def get_(self):
        """Get a motor parameter.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        raise NotImplementedError

class Motor(BaseMotor):
    """Generic motor that exposes the controller command dictionaries."""
    def __init__(self, controller, address="0", debug=False):
        """Initialize a generic addressed motor."""
        super().__init__(controller, address=address, debug=debug)
    
    def move(self, req="relative", data="0"):
        """Function initiate motor movement.

        Parameters
        ----------
        req : str, optional
            Name of request
        data : str, optional
            Parameters to be sent after address and request

        Returns
        -------
        status : tuple
            (code, addr, data)
        """

        if req in mov_:
            instruction = mov_[req]
        else:
            print(f"Invalid Command: {req}")
            return False

        status = self.send_command(instruction, message=data)

        return status
    
    def get(self, req="settings", data=""):
        """Generates the GET commands from get_ cmd dictionary.

        Parameters
        ----------
        req : str, optional
            Name of request
        data : str, optional
            Parameters to be sent after address and request

        Returns
        -------
        status : tuple
            (code, addr, data)
        """

        if req in get_:
            instruction = get_[req]
        else:
            print(f"Invalid Command: {req}")
            return None

        status = self.send_command(instruction, message=data)

        return status

    def set(self, req="", data=""):
        """Generates the SET commands from set_ cmd dictionary.

        Parameters
        ----------
        req : str, optional
            Name of request
        data : str, optional
            Parameters to be sent after address and request

        Returns
        -------
        status : tuple
            (code, addr, data)
        """

        if req in set_:
            instruction = set_[req]
        else:
            print(f"Invalid Command: {req}")
            return None

        status = self.send_command(instruction, message=data)

        return status

class CustomMotor(Motor):
    """High-level stepper motor interface for the SMIS controller."""

    def __init__(self, controller, address="0", debug=False, steps_per_rev=400):
        """Initialize a motor and query its initial position and settings.

        Parameters
        ----------
        controller : BaseSerialController
            Controller used for communication.
        address : str, default="0"
            Motor address.
        debug : bool, default=False
            Whether to print communication diagnostics.
        steps_per_rev : int, default=400
            Physical full steps per motor revolution.
        """
        super().__init__(controller, address=address, debug=debug)

        self.last_dir = None
        self.position = None
        self.last_position = None

        # Important settings of the physical motor and controller
        self.steps_per_rev = steps_per_rev  # Step per revolution - physical property of the stepper motor
        self.microsteps_per_step = None # Microstep per step settings of the driver
        self.microsteps_per_rev = None
        self.max_velocity = None # Maximum velocity for the movement in ramp and soft mode
        self.max_acceleration = None # Maximum acceleration for ramp and soft mode
        self.target_velocity = 0 # Velocity in speed mode
        self.move_mode = move_modes.ramp
        self.is_moving = False

        self.get_position()
        self.get_settings()

    # Wrapper functions
    def move_relative(self, pos=0, wait=False):
        """Move by a relative number of controller steps.

        Parameters
        ----------
        pos : int, default=0
            Signed relative displacement in steps.
        wait : bool, default=False
            Wait until the controller reports that movement has stopped.

        Returns
        -------
        bool or None
            Whether the motor is still moving, or ``None`` for an unexpected response.
        """
        new_dir = bool(pos>=0)
        
        code, addr, data = self.move(req="relative",data=str(pos))

        if code == "MO":
            self.last_dir = new_dir
            moving = bool(data[0])
            if wait:
                while moving:
                    moving = self.get_status()

            return moving
        
        return None
    
    def move_absolute(self, pos=0, wait=False):
        """Move to an absolute controller position in steps.

        Parameters
        ----------
        pos : int, default=0
            Target position in steps.
        wait : bool, default=False
            Wait until the controller reports that movement has stopped.

        Returns
        -------
        bool or None
            Whether the motor is still moving, or ``None`` for an unexpected response.
        """
        self.get_position()
        new_dir = bool(pos>=self.position)

        code, addr, data = self.move(req="absolute",data=str(pos))

        if code == "MO":
            self.last_dir = new_dir
            moving = bool(data[0])
            if wait:
                while moving:
                    moving = self.get_status()

            return moving
        
        return None

    def get_position(self):
        """Read and cache the motor position in controller steps.

        Returns
        -------
        int or None
            Current position, or ``None`` if the response code is unexpected.
        """
        code, addr, data = self.get(req="position")
        new_position = data[0]
        if code == "PO":
            if new_position != self.position:
                self.last_position = self.position
            self.position = new_position
            return new_position
        
        return None

    def get_settings(self):
        """Read and cache microstepping, velocity, and acceleration settings.

        Returns
        -------
        list of int or None
            Raw settings in the order returned by the controller.
        """
        code, addr, data = self.get(req="settings")
        if code == "MV":
            self.microsteps_per_step = data[0]
            self.microsteps_per_rev = self.microsteps_per_step*self.steps_per_rev
            self.max_velocity = data[1]
            self.max_acceleration = data[2]
            self.target_velocity = data[3]
            return data

        return None
    
    def get_switch_states(self):
        """Read the left and right limit-switch states.

        Returns
        -------
        tuple of int or None
            ``(left_state, right_state)`` or ``None`` for an unexpected response.
        """
        code, addr, data = self.get(req="switchstate")
        if code == "SS":
            Lswitch = data[0]
            Rswitch = data[1]
            return Lswitch, Rswitch
        
        return None

    def get_status(self):
        """Read whether the motor is currently moving.

        Returns
        -------
        bool or None
            Movement state, or ``None`` for an unexpected response.
        """
        code, addr, data = self.get(req="status")
        if code == "MO":
            self.is_moving = bool(data[0])
            return bool(data[0])
        
        return None
    
    def set_position(self, pos = 0):
        """Set the controller's current and target position.

        Parameters
        ----------
        pos : int, default=0
            Position in controller steps.

        Returns
        -------
        int or None
            New position, or ``None`` for an unexpected response.
        """
        code, addr, data = self.set(req="position",data=str(pos))
        position = data[0]
        if code == "PO":
            self.last_position = position
            self.position = position
            return position
        
        return None
    
    def set_switches(self, state = True):
        """Enable or disable the motor's limit-switch stops.

        Parameters
        ----------
        state : bool, default=True
            Whether switch stops should be enabled.

        Returns
        -------
        tuple of int or None
            Left and right switch states, or ``None`` for an unexpected response.
        """
        code, addr, data = self.set(req="motorswitch",data=str(int(state)))
        if code == "SS":
            Lswitch = data[0]
            Rswitch = data[1]
            return Lswitch, Rswitch
        
        return None
    
    def set_mode(self, mode = move_modes.ramp):
        """Set the controller movement mode.

        Parameters
        ----------
        mode : move_modes, default=move_modes.ramp
            TMC429 mode to use.

        Returns
        -------
        int or None
            Controller mode value, or ``None`` for an unexpected response.
        """
        code, addr, data = self.set(req="mode",data=str(mode.value))
        if code == "MM":
            self.move_mode = move_modes(data[0])
            return data[0]
        
        return None
    
    def set_microsteps(self, ms_per_step = 8):
        """Set microstepping and preserve the current physical position.

        Parameters
        ----------
        ms_per_step : int, default=8
            Supported microstep factor: 1, 2, 4, 8, 16, 32, 64, 128, or 256.

        Returns
        -------
        int or None
            Updated microsteps-per-step value, or ``None`` for an invalid factor
            or unexpected response.
        """
        microsteps_list = [1, 2, 4, 8, 16, 32, 64, 128, 256]
        
        if ms_per_step in microsteps_list:
            self.get_settings()
            oldpos = self.get_position()
            newpos = int(oldpos*(ms_per_step/self.microsteps_per_step))
            code, addr, data = self.set(req="microsteps", data=str(ms_per_step))
            if code == "MS":
                self.set_position(newpos)
                data = self.get_settings()
                return data[0]
            
            return None
        
        return None
    
    def set_maxvelocity(self, vmax = 6400):
        """Set maximum velocity for soft and ramp modes.

        Parameters
        ----------
        vmax : int, default=6400
            Maximum velocity in steps per second.

        Returns
        -------
        int or None
            Applied velocity, or ``None`` for an unexpected response.
        """
        code, addr, data = self.set(req="maxspeed", data=str(vmax))
        if code == "VM":
            self.max_velocity = data[0]
            return data[0]
       
        return None
    
    def set_maxacceleration(self, amax = 12800):
        """Set maximum acceleration for soft and ramp modes.

        Parameters
        ----------
        amax : int, default=12800
            Maximum acceleration in steps per second squared.

        Returns
        -------
        int or None
            Applied acceleration, or ``None`` for an unexpected response.
        """
        code, addr, data = self.set(req="maxacceleration", data=str(amax))
        if code == "AM":
            self.max_acceleration = data[0]
            return data[0]
        
        return None
    
    def set_targetvelocity(self, speed = 0):
        """Set target speed for velocity mode.

        Parameters
        ----------
        speed : int, default=0
            Target speed in steps per second; the controller limit is 2047.

        Returns
        -------
        int or None
            Applied target speed, or ``None`` for an unexpected response.
        """
        code, addr, data = self.set(req="targetspeed", data=str(speed))
        if code == "VT":
            self.target_velocity = data[0]
            return data[0]
        
        return None

    def home(self):
        """Request the motor's home movement."""
        self.move("home")

    def autotune(self):
        """Run the driver's automatic tuning procedure.

        Returns
        -------
        list of int or None
            Autotuning result data, or ``None`` for an unexpected response.
        """
        code, addr, data = self.move(req="autotune",data=None)
        if code == "AT":
            return data

    def change_address(self, new_address):
        """Change the motor address and update this object's address.

        Parameters
        ----------
        new_address : str
            New controller address.

        Returns
        -------
        tuple or None
            Controller response status.
        """
        old_address = self.address
        status = self.set("address", data=new_address)
        if status[0] == new_address:
            # Make the Motor object know about the change
            self.address = new_address
            if self.debug:
                print(f"Address successfully changed from {old_address} to {new_address}.")

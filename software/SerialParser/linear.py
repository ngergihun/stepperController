"""Module for linear stages. """
from . import CustomMotor


class Linear(CustomMotor):
    """Stepper motor wrapper that converts between steps and linear distance."""

    def __init__(self, controller, address="0", debug=False):
        """Initialize a linear motor with a 1 mm/revolution thread pitch."""
        super().__init__(controller=controller, address=address, debug=debug)

        self.threadpitch = 1.0 # mm/rev
        self.wait_movement = False

    ## Setting and getting positions

    def move_to(self, distance):
        """Move to an absolute linear position.

        Parameters
        ----------
        distance : float
            Target distance in micrometers.

        Returns
        -------
        bool or None
            Movement state returned by :meth:`CustomMotor.move_absolute`.
        """
        steps = distance_to_steps(distance,threadpitch=self.threadpitch,steps_per_rev=self.microsteps_per_rev)
        status = self.move_absolute(pos=steps, wait=self.wait_movement)
        
        return status

    def move_distance(self, distance):
        """Move by a relative linear distance.

        Parameters
        ----------
        distance : float
            Signed displacement in micrometers.

        Returns
        -------
        bool or None
            Movement state returned by :meth:`CustomMotor.move_relative`.
        """
        steps = distance_to_steps(distance,threadpitch=self.threadpitch,steps_per_rev=self.microsteps_per_rev)
        status = self.move_relative(pos=steps, wait=self.wait_movement)
        
        return status
    
    def get_distance(self):
        """Return the current linear position in micrometers.

        Returns
        -------
        float
            Current position converted from controller steps.
        """
        pos = self.get_position()
        distance = steps_to_distance(pos,threadpitch=self.threadpitch,steps_per_rev=self.microsteps_per_rev)
        
        return distance

    def jog(self, direction="forward", speed=0.0):
        """Set velocity-mode jogging speed in a selected direction.

        Parameters
        ----------
        direction : {"backward", "forward"}, default="forward"
            Jogging direction.
        speed : float, default=0.0
            Jog speed in micrometers per second.

        Returns
        -------
        tuple or None
            Current motor status, or ``None`` for an invalid direction.
        """
        speed_steps = int(distance_to_steps(speed,threadpitch=self.threadpitch,steps_per_rev=self.microsteps_per_rev))
        
        if speed_steps > 2047:
            speed_steps = 2047
        
        if direction in ["backward", "forward"]:
            if direction == "backward":
                self.set_targetvelocity(speed=-1*speed_steps)
                status = self.get_status()
                return status
            else:
                self.set_targetvelocity(speed=speed_steps)
                status = self.get_status()
                return status
        else:
            return None
        
    # Set the speed and acceleration
    def set_speed(self, speed, threadpitch=1.0, steps_per_rev=3200):
        """Set maximum speed and acceleration from a linear speed.

        Parameters
        ----------
        speed : float
            Maximum speed in micrometers per second.
        threadpitch : float, default=1.0
            Screw pitch in millimeters per revolution.
        steps_per_rev : int, default=3200
            Controller steps per revolution.
        """
        step_speed = int(speed/(threadpitch*1000)*steps_per_rev)
        self.set_maxvelocity(vmax=step_speed)
        self.set_maxacceleration(amax=4*step_speed)

# Helper functions

def steps_to_distance(steps, threadpitch=1.0, steps_per_rev=3200):
    """Convert controller steps to linear distance.

    Parameters
    ----------
    steps : int or float
        Number of controller steps.
    threadpitch : float, default=1.0
        Screw pitch in millimeters per revolution.
    steps_per_rev : int, default=3200
        Controller steps per revolution.

    Returns
    -------
    float
        Distance in micrometers.
    """
    distance = steps/steps_per_rev*threadpitch*1000
    return distance

def distance_to_steps(distance, threadpitch=1.0, steps_per_rev=3200):
    """Convert linear distance to an integer step count.

    Parameters
    ----------
    distance : float
        Distance in micrometers.
    threadpitch : float, default=1.0
        Screw pitch in millimeters per revolution.
    steps_per_rev : int, default=3200
        Controller steps per revolution.

    Returns
    -------
    int
        Truncated controller step count.
    """
    revs = distance / (threadpitch*1000)
    steps = int(revs*steps_per_rev)

    # moved_dist = steps/steps_per_rev*threadpitch*1000

    return steps

def calc_threadpitch(steps, distance, steps_per_rev=3200):
    """Calculate screw pitch from measured steps and distance.

    Parameters
    ----------
    steps : int or float
        Number of controller steps measured.
    distance : float
        Measured distance in micrometers.
    steps_per_rev : int, default=3200
        Controller steps per revolution.

    Returns
    -------
    float
        Screw pitch in millimeters per revolution.
    """
    revs = steps/steps_per_rev

    threadpitch = distance/revs/1000

    return threadpitch
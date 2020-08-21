
import math

"""
Class for two-joint arm (composed of a 'bicep' and 'forearm') simulation
that moves per proper kinematics and user-imposed angle restrictions on the arm segments.
"""
class TwoJointArm:
    precision = 6  # number of decimal places properties
    def __init__(self, bicep_length: float, forearm_length: float, bicep_angle=70, forearm_angle=90,
                 bicep_angle_limit=None, forearm_angle_limit=None):
        """
        Required params:
        :param bicep_length: first arm segment length (units must be same as forearm_length)
        :param forearm_length: second arm segment length (units must be same as bicep_length)

        Optional params:
        :param bicep_angle: initial angle for bicep in degrees
        :param forearm_angle: initial angle for forearm in degrees
        :param bicep_angle_limit: absolute angle limitation (exclusive) for bicep
        :param forearm_angle_limit: absolute angle limitation (exclusive) for forearm
        """
        self.bicep_length = bicep_length
        self.forearm_length = forearm_length
        self.bicep_angle = bicep_angle
        self.forearm_angle = forearm_angle
        elbow, hand = self._solve_joints(self.bicep_angle, self.forearm_angle)
        self.bicep_angle_limit = bicep_angle_limit
        self.forearm_angle_limit = forearm_angle_limit
        self._set_joints(elbow, hand)

    def _solve_joints(self, bicep_angle: float, forearm_angle: float):
        """
        Forward kinematics calculation. Given the angles, will move elbow joint
        and the hand (end of forearm) such that they will have the given angles.
        :param bicep_angle: desired angle in degrees
        :param forearm_angle: desired angle in degrees
        :return: 2 float tuples for (x,y) coordinates of elbow and hand after move
        """
        bicep_length_x = self.bicep_length*math.cos(math.radians(bicep_angle))
        bicep_length_y = self.bicep_length*math.sin(math.radians(bicep_angle))
        forearm_length_x = self.forearm_length*math.cos(math.radians(bicep_angle + forearm_angle))
        forearm_length_y = self.forearm_length*math.sin(math.radians(bicep_angle + forearm_angle))
        elbow = (bicep_length_x, bicep_length_y)
        hand = (bicep_length_x + forearm_length_x, bicep_length_y + forearm_length_y)
        return elbow, hand

    def move_to(self, position: tuple, sign: int):
        """
        Moves arm to given location if arm can reach it. Sets the angles of the arm
        per inverse kinematics calculations. Sign determines whether the elbow is bent
        upward ^ or downward like upside down carrot (if forearm angle is 0, no bending).

        :param position: (x,y) float tuple location
        :param sign: -1 bends elbow upward ^, 1 bends the opposite way
        :return: 1 if arm can reach the location, 0 if cannot
        """
        bicep_angle, forearm_angle = self._solve_inverse_kinematics(position, sign)
        # could not reach position
        if (bicep_angle, forearm_angle) == (None, None):
            return 0
        else:
            self._set_angles(bicep_angle, forearm_angle)
            new_elbow, new_hand = self._solve_joints(bicep_angle, forearm_angle)
            self._set_joints(new_elbow, new_hand)
            return 1

    def _set_angles(self, bicep_angle: float, forearm_angle: float):
        self.bicep_angle = bicep_angle
        self.forearm_angle = forearm_angle

    def get_angles(self):
        return self.bicep_angle, self.forearm_angle

    def _set_joints(self, elbow: tuple, hand: tuple):
        self.elbow = elbow
        self.hand = hand

    def _solve_inverse_kinematics(self, position: tuple, sign: int) -> tuple:
        """
        Calculates the inverse kinematics parameters (two angles in degrees)
        necessary to reach goal position.
        Assumes:
         1. goal position is in same units as the arm segment lengths.
         2. position is with respect to the first (shoulder) joint

        :param position: tuple of two floats representing goal position (x,y)
        :param sign: -1 bends elbow upward ^, 1 bends the opposite way
        :return: tuple: angles in degrees for first and second arm segment, respectively,
         necessary to reach goal position.
        Otherwise, returns (None, None) if goal not possible.
        """
        failed = (None, None)
        if not self.can_reach(position):
            return failed

        forearm_angle = self._solve_forearm_angle(position, sign)
        bicep_angle = self._solve_bicep_angle(position, forearm_angle)

        angles = math.degrees(bicep_angle), math.degrees(forearm_angle)
        if self.bicep_angle_limit or self.forearm_angle_limit:
            if abs(angles[0]) >= self.bicep_angle_limit or abs(angles[1]) >= self.forearm_angle_limit:
                return failed
        return angles

    def _solve_forearm_angle(self, position: tuple, sign: int):
        """
        Calculates the forearm angle necessary to reach goal position.
        """
        x = position[0]
        y = position[1]
        # use law of cosines to get cos(angle) between bicep and forearm
        # this angle is the complement of the forearm angle, so negate it to get
        # cosine(forearm_angle)
        cosine_of_forearm_angle = (x ** 2 + y ** 2 - self.bicep_length ** 2 - self.forearm_length ** 2) / \
                                  (2 * self.bicep_length * self.forearm_length)
        # make sure input is between [-1, 1]
        cosine_of_forearm_angle = put_in_inverse_trig_range(cosine_of_forearm_angle)
        # forearm_angle is negated so arm goes over-hand, not under-hand
        forearm_angle = sign * math.acos(cosine_of_forearm_angle)

        return forearm_angle

    def _solve_bicep_angle(self, position: tuple, forearm_angle: float):
        """
        Calculates the bicep angle necessary to reach goal position.
        """
        x = position[0]
        y = position[1]
        # arm_triangle is the right triangle created when using the bicep as
        # the triangle base (and x-axis) and the height of the hand from this axis to the (x,y)
        # goal position as the vertical side, which must be a function of the forearm angle
        arm_triangle_base = self.bicep_length + self.forearm_length*math.cos(forearm_angle)
        arm_triangle_height = self.forearm_length*math.sin(forearm_angle)
        arm_triangle_base_angle = math.atan2(arm_triangle_height, arm_triangle_base)

        # goal_triangle is the right triangle created by using the x coordinate of
        # the goal position as the triangle base and the y coordinate as the vertical side
        goal_triangle_base_angle = math.atan2(y, x)

        # the difference between these angles yields the bicep angle
        bicep_angle = goal_triangle_base_angle-arm_triangle_base_angle

        return bicep_angle

    def can_reach(self, position: tuple) -> bool:
        """
        Determines if position is outside of the arm's radius. If so,
        function returns False to indicate arm cannot reach, otherwise returns True.
        :param position: float tuple for position coordinates (x,y)
        """
        x = position[0]
        y = position[1]
        dist_to_shoulder = math.sqrt(x**2 + y**2)
        max_dist = self.bicep_length + self.forearm_length
        if dist_to_shoulder > max_dist:
            return False
        return True

    def __str__(self):
        return "bicep_length: {0}, forearm_length: {1},\nElbow: {2},\nHand: {3},\nbicep_angle: {4}, forearm_angle: {5}".format(
            self.bicep_length, self.forearm_length, self.elbow, self.hand, self.bicep_angle, self.forearm_angle
        )

def put_in_inverse_trig_range(length: float):
    """
    Forces length to be in [-1,1] range if not already so that inverse
    trigonometry operations can yield valid answers.
    :param length:
    :return: -1 if length less than -1, 1 if greater than 1, otherwise itself
    """
    if length < -1:
        return -1
    if length > 1:
        return 1
    return length

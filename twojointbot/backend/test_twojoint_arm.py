# tests TwoJointArm class
from backend.twojoint_arm import TwoJointArm
import math

def test_solve_inverse_kinematics():
    arm = TwoJointArm(4.6, 4.6)
    sign = 1
    actual = arm._solve_inverse_kinematics((arm.bicep_length+arm.forearm_length+.01, 0), sign)
    assert actual == (None, None)
    assert arm._solve_inverse_kinematics((arm.bicep_length+arm.forearm_length, 0), sign) != (None, None)
    assert arm._solve_inverse_kinematics((arm.bicep_length+arm.forearm_length - 2, 1), sign) != (None, None)
    arm2 = TwoJointArm(8.2, .8)
    assert arm2._solve_inverse_kinematics((9, 0), sign) == (0, 0)
    arm2.move_to((9, 0), sign)
    assert arm2._solve_inverse_kinematics((9, 0), sign) == arm2.get_angles()
    assert arm2._solve_inverse_kinematics((8.2, .8), sign) == (0, 90)
    bicep_angle, forearm_angle = arm2._solve_inverse_kinematics((9, 0), sign)
    assert arm2._solve_joints(bicep_angle, forearm_angle) == ((8.2, 0), (9, 0))
    arm2.move_to((8.2, .8), sign)
    assert arm2._solve_inverse_kinematics((8.2, .8), sign) == arm2.get_angles()
    bicep_angle, forearm_angle = arm2._solve_inverse_kinematics((8.2, 0.8), sign)
    assert arm2._solve_joints(bicep_angle, forearm_angle) == ((8.2, 0), (8.2, .8))
    assert arm2._solve_inverse_kinematics((0, 9), sign) == (90, 0)
    arm3 = TwoJointArm(400, 300)
    assert arm3._solve_inverse_kinematics((700, 0), sign) == (0, 0)
    arm3.move_to((700, 0), sign)
    assert arm3._solve_inverse_kinematics((700, 0), sign) == arm3.get_angles()
    assert arm3._solve_inverse_kinematics((400, 300), sign) == (0, 90)
    bicep_angle, forearm_angle = arm3._solve_inverse_kinematics((700, 0), sign)
    assert arm3._solve_joints(bicep_angle, forearm_angle) == ((400, 0), (700, 0))
    arm3.move_to((400, 300), sign)
    assert arm3._solve_inverse_kinematics((400, 300), sign) == arm3.get_angles()
    bicep_angle, forearm_angle = arm3._solve_inverse_kinematics((400, 300), sign)
    assert arm3._solve_joints(bicep_angle, forearm_angle) == ((400, 0), (400, 300))
    assert arm3._solve_inverse_kinematics((0, 700), sign) == (90, 0)

def test_can_reach():
    arm = TwoJointArm(8.2, .77)
    assert not arm.can_reach((arm.bicep_length+arm.forearm_length+.01, 0))
    assert arm.can_reach((arm.bicep_length+arm.forearm_length, 0))
    assert arm.can_reach((arm.bicep_length+arm.forearm_length - 2, 1))

def test_thorough():
    arms = (TwoJointArm(4.6, 4.6), TwoJointArm(8.2, .8), TwoJointArm(400, 300))
    sign = 1
    for idx, arm in enumerate(arms):
        l1 = arm.bicep_length
        l2 = arm.forearm_length
        r = l1+l2
        locations = []
        angles = [0, 20, 30, 45, 60, 80, 100, 180, 200, 360]
        for ang in angles:
            locations.append((r*math.cos(math.radians(ang)), r*math.sin(math.radians(ang))))
        for idx_angle, location in enumerate(locations):
            arm.move_to(location, sign)
            positive_bicep_angle = arm.bicep_angle if arm.bicep_angle >= 0 else arm.bicep_angle + 360
            assert abs(arm.hand[0] - location[0]) < .05 and abs(arm.hand[1] - location[1]) < .05
            assert abs(positive_bicep_angle - angles[idx_angle]) < 2
        locations = [(l1, l2)]
        for location in locations:
            arm.move_to(location, sign)
            assert abs(arm.hand[0] - location[0]) < .05 and abs(arm.hand[1] - location[1]) < .05

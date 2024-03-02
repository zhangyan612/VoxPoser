import numpy as np
from env_utils import execute, reset_to_default_pose

from perception_utils import parse_query_obj
from plan_utils import get_affordance_map, get_avoidance_map, get_velocity_map, get_rotation_map, get_gripper_map
import numpy as np

# from transforms3d.euler import euler2quat, quat2euler, qinverse, qmult

from interfaces import *
from LMP import parse_query_obj





# Grabbing 

 # code to execute:
objects = ['bin', 'rubbish', 'tomato1', 'tomato2']
composer("grasp the rubbish")
composer("move to 20cm above the bin")
composer("open gripper")
composer("move to 20cm above the bin")
composer("close gripper")
composer("move to 20cm above the bin")
composer("open gripper")

 # code to execute:
movable = parse_query_obj('gripper')
affordance_map = get_affordance_map('a point at the center of the rubbish')
gripper_map = get_gripper_map('open everywhere except 1cm around the rubbish')
execute(movable, affordance_map=affordance_map, gripper_map=gripper_map)

 # code to execute:
def ret_val():
    objects = ['bin', 'rubbish', 'tomato1', 'tomato2']
    gripper = detect('gripper')
    return gripper

 # code to execute:
def ret_val():
    affordance_map = get_empty_affordance_map()
    rubbish = parse_query_obj('rubbish')
    x, y, z = rubbish.position
    affordance_map[x, y, z] = 1
    return affordance_map

 # code to execute:
def ret_val():
    # open everywhere except 1cm around the rubbish
    gripper_map = get_empty_gripper_map()
    # open everywhere
    gripper_map[:, :, :] = 1
    # close when 1cm around the rubbish
    rubbish = parse_query_obj('rubbish')
    set_voxel_by_radius(gripper_map, rubbish.position, radius_cm=1, value=0)
    return gripper_map

 # code to execute:
def ret_val():
    objects = ['bin', 'rubbish', 'tomato1', 'tomato2']
    rubbish = detect('rubbish')
    return rubbish

 # code to execute:
def ret_val():
    objects = ['bin', 'rubbish', 'tomato1', 'tomato2']
    rubbish = detect('rubbish')
    return rubbish



movable = parse_query_obj('gripper')
affordance_map = get_affordance_map('a point 20cm above the bin')
execute(movable, affordance_map=affordance_map)

# {
# 'euler2quat': <function euler2quat at 0x7fc809597310>, 
# 'quat2euler': <function quat2euler at 0x7fc8095973a0>, 
# 'qinverse': <function qinverse at 0x7fc8095918b0>, 
# 'qmult': <function qmult at 0x7fc809591670>, 
# 'cm2index': <bound method LMP_interface.cm2index of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>,
# 'detect': <bound method LMP_interface.detect of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'execute': <bound method LMP_interface.execute of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'get_ee_pos': <bound method LMP_interface.get_ee_pos of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'get_empty_affordance_map': <bound method LMP_interface.get_empty_affordance_map of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'get_empty_avoidance_map': <bound method LMP_interface.get_empty_avoidance_map of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'get_empty_gripper_map': <bound method LMP_interface.get_empty_gripper_map of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'get_empty_rotation_map': <bound method LMP_interface.get_empty_rotation_map of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'get_empty_velocity_map': <bound method LMP_interface.get_empty_velocity_map of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'index2cm': <bound method LMP_interface.index2cm of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'pointat2quat': <bound method LMP_interface.pointat2quat of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'reset_to_default_pose': <bound method LMP_interface.reset_to_default_pose of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'set_voxel_by_radius': <bound method LMP_interface.set_voxel_by_radius of <interfaces.LMP_interface object at 0x7fc7bc5c9bb0>>, 
# 'parse_query_obj': <LMP.LMP object at 0x7fc7bc5c9ca0>, 
# 'get_affordance_map': <LMP.LMP object at 0x7fc7bc5c9e50>, 
# 'get_avoidance_map': <LMP.LMP object at 0x7fc7bc5c9cd0>, 
# 'get_velocity_map': <LMP.LMP object at 0x7fc7bc5c9f10>, 
# 'get_rotation_map': <LMP.LMP object at 0x7fc7bc5c9fa0>, 
# 'get_gripper_map': <LMP.LMP object at 0x7fc7bc5c9e80>, 
# 'composer': <LMP.LMP object at 0x7fc7bc5c9d30>, 
# 'exec': <function exec_safe.<locals>.<lambda> at 0x7fc7940d7700>, 
# 'eval': <function exec_safe.<locals>.<lambda> at 0x7fc7940d7700>
# }
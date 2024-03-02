import openai
from arguments import get_config
from interfaces import setup_LMP
from visualizers import ValueMapVisualizer
from envs.rlbench_env import VoxPoserRLBench
from utils import set_lmp_objects, DynamicObservation
import numpy as np
from rlbench import tasks
import configparser

config = configparser.ConfigParser()
config.read('.env')

openai.api_base = config.get('openai', 'base_url')
openai.api_key = config.get('openai', 'api_key')

config = get_config('rlbench')

# initialize env and voxposer ui
visualizer = ValueMapVisualizer(config['visualizer'])
env = VoxPoserRLBench(visualizer=visualizer)
lang_model_programs, lmp_env = setup_LMP(env, config, debug=False)
voxposer_ui = lang_model_programs['plan_ui']

# below are the tasks that have object names added to the "task_object_names.json" file
# uncomment one to use
env.load_task(tasks.PutRubbishInBin)
# env.load_task(tasks.LampOff)
# env.load_task(tasks.OpenWineBottle)
# env.load_task(tasks.PushButton)
# env.load_task(tasks.TakeOffWeighingScales)
# env.load_task(tasks.MeatOffGrill)
# env.load_task(tasks.SlideBlockToTarget)
# env.load_task(tasks.TakeLidOffSaucepan)
# env.load_task(tasks.TakeUmbrellaOutOfUmbrellaStand)

descriptions, obs = env.reset()
set_lmp_objects(lang_model_programs, env.get_object_names())  # set the object names to be used by voxposer

# instruction = np.random.choice(descriptions)
# print(descriptions)
# print(obs)
# voxposer_ui(instruction)

def gripper_func():
    objects = ['bin', 'rubbish', 'tomato1', 'tomato2']
    gripper = lmp_env.detect('gripper')
    return gripper


def affordance_map_func():
    affordance_map = lmp_env.get_empty_affordance_map()
    rubbish = lmp_env.detect('rubbish')
    x, y, z = rubbish.position
    affordance_map[x, y, z] = 1
    return affordance_map

def gripper_map_func():
    # open everywhere except 1cm around the rubbish
    gripper_map = lmp_env.get_empty_gripper_map()
    # open everywhere
    gripper_map[:, :, :] = 1
    # close when 1cm around the rubbish
    rubbish = lmp_env.detect('rubbish')
    lmp_env.set_voxel_by_radius(gripper_map, rubbish.position, radius_cm=1, value=0)
    return gripper_map


lmp_env.execute(gripper_func, affordance_map=affordance_map_func, gripper_map=gripper_map_func)

# execute
# cm2index
# get_empty_affordance_map


# lmp_env.detect('gripper')
# {'name': 'gripper', 'position': array([52, 49, 71], dtype=int32), 'aabb': array([[52, 49, 71],
# [52, 49, 71]], dtype=int32), '_position_world': array([ 0.27846646, -0.00815974,  1.47197688])}


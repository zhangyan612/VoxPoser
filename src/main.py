import openai
from arguments import get_config
from interfaces import setup_LMP
from visualizers import ValueMapVisualizer
from envs.rlbench_env import VoxPoserRLBench
from utils import set_lmp_objects
import numpy as np
from rlbench import tasks
import configparser

config = configparser.ConfigParser()
config.read('.env')

openai.api_base = config.get('openai', 'base_url')
openai.api_key = config.get('openai', 'api_key')

config = get_config('rlbench')
# uncomment this if you'd like to change the language model (e.g., for faster speed or lower cost)
for lmp_name, cfg in config['lmp_config']['lmps'].items():
    cfg['model'] = 'mixtral-8x7b'

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

instruction = np.random.choice(descriptions)
print(instruction)
# voxposer_ui(instruction)

## VoxPoser: Composable 3D Value Maps for Robotic Manipulation with Language Models

#### [[Project Page]](https://voxposer.github.io/) [[Paper]](https://voxposer.github.io/voxposer.pdf) [[Video]](https://www.youtube.com/watch?v=Yvn4eR05A3M)

[Wenlong Huang](https://wenlong.page)<sup>1</sup>, [Chen Wang](https://www.chenwangjeremy.net/)<sup>1</sup>, [Ruohan Zhang](https://ai.stanford.edu/~zharu/)<sup>1</sup>, [Yunzhu Li](https://yunzhuli.github.io/)<sup>1,2</sup>, [Jiajun Wu](https://jiajunwu.com/)<sup>1</sup>, [Li Fei-Fei](https://profiles.stanford.edu/fei-fei-li)<sup>1</sup>

<sup>1</sup>Stanford University, <sup>2</sup>University of Illinois Urbana-Champaign

<img  src="media/teaser.gif" width="550">

This is the official demo code for [VoxPoser](https://voxposer.github.io/), a method that uses large language models and vision-language models to zero-shot synthesize trajectories for manipulation tasks.

In this repo, we provide the implementation of VoxPoser in [RLBench](https://sites.google.com/view/rlbench) as its task diversity best resembles our real-world setup. Note that VoxPoser is a zero-shot method that does not require any training data. Therefore, the main purpose of this repo is to provide a demo implementation rather than an evaluation benchmark.

If you find this work useful in your research, please cite using the following BibTeX:

```bibtex
@article{huang2023voxposer,
      title={VoxPoser: Composable 3D Value Maps for Robotic Manipulation with Language Models},
      author={Huang, Wenlong and Wang, Chen and Zhang, Ruohan and Li, Yunzhu and Wu, Jiajun and Fei-Fei, Li},
      journal={arXiv preprint arXiv:2307.05973},
      year={2023}
    }
```

## Setup Instructions

Note that this codebase is best run with a display. For running in headless mode, refer to the [instructions in RLBench](https://github.com/stepjam/RLBench#running-headless).

- Create a conda environment:
```Shell
conda create -n voxposer-env python=3.9
conda activate voxposer-env
```

- See [Instructions](https://github.com/stepjam/RLBench#install) to install PyRep and RLBench (Note: install these inside the created conda environment).

- Install other dependencies:
```Shell
pip install -r requirements.txt
```

- Obtain an [OpenAI API](https://openai.com/blog/openai-api) key, and put it inside the first cell of the demo notebook.

## Running Demo

Demo code is at `src/playground.ipynb`. Instructions can be found in the notebook.

## Code Structure

Core to VoxPoser:

- **`playground.ipynb`**: Playground for VoxPoser.
- **`LMP.py`**: Implementation of Language Model Programs (LMPs) that recursively generates code to decompose instructions and compose value maps for each sub-task.
- **`interfaces.py`**: Interface that provides necessary APIs for language models (i.e., LMPs) to operate in voxel space and to invoke motion planner.
- **`planners.py`**: Implementation of a greedy planner that plans a trajectory (represented as a series of waypoints) for an entity/movable given a value map.
- **`controllers.py`**: Given a waypoint for an entity/movable, the controller applies (a series of) robot actions to achieve the waypoint.
- **`dynamics_models.py`**: Environment dynamics model for the case where entity/movable is an object or object part. This is used in `controllers.py` to perform MPC.
- **`prompts/rlbench`**: Prompts used by the different Language Model Programs (LMPs) in VoxPoser.

Environment and utilities:

- **`envs`**:
  - **`rlbench_env.py`**: Wrapper of RLBench env to expose useful functions for VoxPoser.
  - **`task_object_names.json`**: Mapping of object names exposed to VoxPoser and their corresponding scene object names for each individual task.
- **`configs/rlbench_config.yaml`**: Config file for all the involved modules in RLBench environment.
- **`arguments.py`**: Argument parser for the config file.
- **`LLM_cache.py`**: Caching of language model outputs that writes to disk to save cost and time.
- **`utils.py`**: Utility functions.
- **`visualizers.py`**: A Plotly-based visualizer for value maps and planned trajectories.

## Acknowledgments
- Environment is based on [RLBench](https://sites.google.com/view/rlbench).
- Implementation of Language Model Programs (LMPs) is based on [Code as Policies](https://code-as-policies.github.io/).
- Some code snippets are from [Where2Act](https://cs.stanford.edu/~kaichun/where2act/).
- Additional acknowledgement to GitHub Copilot and GPT-4 for collaboratively writing a significant portion of the code in this codebase.

# Process
1. detect end effoctor/gripper location
2. detect object and get it's location
3. generate way point from end effector to object location
4. optimize waypoint and execute the plan
5. save executed plan to visulization



summary of how the main code works:

Load configuration from file using get_config(). This returns a ConfigDict that allows accessing config through attributes.
Initialize the ValueMapVisualizer with the config.
Initialize the VoxPoserRLBench environment with the visualizer. This launches the RLBench scene.
Set up the LMP and voxposer UI using the setup_LMP() function. Passes the env and config.
Load a task into the environment using env.load_task(). This resets task variables and records object IDs.
Reset the environment with env.reset(). This samples a variation and returns descriptions and observations.
Set the object names in the LMP using set_lmp_objects(). This maps instruction object references to environment objects.
Pick a random instruction and pass to the voxposer UI to generate a plan.
So in summary, it:

Configures the environment, LMP, and visualizer
Loads a task and resets the environment
Sets object name mapping for the LMP
Passes an instruction to the LMP to generate a plan
The key steps are setting up the components, loading the task, resetting the environment, and mapping object names before passing instructions to the LMP.

# VLM setup
VLMs and Perception. Given an object/part query from LLMs, we first invoke open-vocab detector
OWL-ViT [15] to obtain a bounding box, then feed it into Segment Anything [118] to obtain a mask,
and finally track the mask using video tracker XMEM [119]. The tracked mask is used with RGB-D
observation to reconstruct the object/part point cloud.


detect(obj name): Takes in an object name and returns a list of dictionaries, where each dictionary
corresponds to one instance of the matching object, containing center position, occupancy grid, and
mean normal vector.

execute(movable,affordance map,avoidance map,rotation map,velocity map,gripper map):
Takes in an “entity of interest” as “movable” (a dictionary returned by detect) and (optionally)
a list of value maps and invokes the motion planner to execute the trajectory. Note that in MPC
settings, “movable” and the input value maps are functions that can be re-evaluated to reflect the
latest environment observation.

cm2index(cm,direction): Takes in a desired offset distance in centimeters along direction and
returns 3-dim vector reflecting displacement in voxel coordinates.
index2cm(index,direction): Inverse of cm2index. Takes in an integer “index” and a “direction”
vector and returns the distance in centimeters in world coordinates displaced by the “integer” in
voxel coordinates.

pointat2quat(vector): Takes in a desired pointing direction for the end-effector and returns a
satisfying target quaternion.

set voxel by radius(voxel map,voxel xyz,radius cm,value): Assigns “value” to voxels
within “radious cm” from “voxel xyz” in “voxel map”.

get empty affordance map(): Returns a default affordance map initialized with 0, where a high
value attracts the entity.

get empty avoidance map(): Returns a default avoidance map initialized with 0, where a high
value repulses the entity.

get empty rotation map(): Returns a default rotation map initialized with current end-effector
quaternion.

get empty gripper map(): Returns a default gripper map initialized with current gripper action,
where 1 indicates “closed” and 0 indicates “open”.

get empty velocity map(): Returns a default affordance map initialized with 1, where the number
represents scale factor (e.g., 0.5 for half of the default velocity).

reset to default pose(): Reset to robot rest pose
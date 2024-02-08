import unittest
import os
import numpy as np
from src.arguments import get_config
from src.visualizers import ValueMapVisualizer

class TestGetConfig(unittest.TestCase):
    def setUp(self):
        CWD_PATH = os.getcwd()
        config_path = CWD_PATH + '/src/configs/rlbench_config.yaml'
        self.config = get_config(config_path=config_path)
        self.visualizer = ValueMapVisualizer(self.config['visualizer'])

    # def test_get_config_default(self):
    #     print(self.config)
    #     self.assertIsInstance(self.config, dict)
    
    # def test_visulizer(self):
    #     visualizer = ValueMapVisualizer(self.config['visualizer'])
    #     print(visualizer)

    def test_update_quality(self):
        self.visualizer.update_quality('low')
        self.assertEqual(self.visualizer.downsample_ratio, 4)
        self.assertEqual(self.visualizer.max_scene_points, 150000)
    
    def test_update_bounds(self):
        lower = np.array([0, 0, 0])
        upper = np.array([1, 1, 1])
        self.visualizer.update_bounds(lower, upper)
        np.testing.assert_array_equal(self.visualizer.workspace_bounds_min, lower)
        np.testing.assert_array_equal(self.visualizer.workspace_bounds_max, upper)

    # def test_visualize(self):
    #     info = {'planner_info': {}, 
    #             'traj_world': [(0, 0, 0), (1, 1, 1)],
    #             'start_pos_world': np.array([0, 0, 0]),
    #             'targets_world': np.array([[1, 1, 1]])}
    #     self.visualizer.visualize(info)
    #     # Just test visualize runs without error
    #     self.assertTrue(True) 


if __name__ == '__main__':
    unittest.main()
import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
#from tf_agents.environments import suite_gym
from tf_agents.trajectories import time_step as ts

tf.compat.v1.enable_v2_behavior()

#class ClueObservation:

class ClueCardCategoryEnv(py_environment.PyEnvironment):

    _num_of_cards: int

    _solution: int
    _tries: int
    
    def __init__(self, num_of_cards = 6):
        self._num_of_cards = num_of_cards
        self._action_spec = array_spec.BoundedArraySpec(shape=(1,), dtype=np.int32, 
                                                        minimum=0, 
                                                        maximum=num_of_cards - 1, 
                                                        name='action')

        self._observation_spec = array_spec.BoundedArraySpec(shape=(1,), dtype=np.int32, 
                                                             minimum=0, name='observation')
        self._state = 0
        self._episode_ended = False
        self._tries = 0
        self._solution = np.random.randint(0, 6)

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self._state = 0
        self._tries = 0
        self._episode_ended = False
        self._solution = np.random.randint(0, 6)
        return ts.restart(np.array([self._state], dtype=np.int32))

    def _step(self, action):
        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        self._tries += 1
        print(action)

        # Make sure episodes don't go on forever.
        if action >= 0 and action < self._num_of_cards:
            self._guess(action)
        else:
            raise ValueError('`action` should be between 0 and ' + str(self._num_of_cards))

        if self._episode_ended or self._state == 1 or self._tries == 10:
            reward = 10 - self._tries
            return ts.termination(np.array([self._state], dtype=np.int32), reward)
        else:
            return ts.transition(np.array([self._state], dtype=np.int32), reward=0.0, discount=1.0)

    def _handle_guess(self):
        pass

    def _guess(self, action):
        if action == self._solution:
            self._state = 1



environment = ClueCardCategoryEnv()
utils.validate_py_environment(environment, episodes=5)

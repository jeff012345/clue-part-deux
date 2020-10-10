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
        # TODO change specs to take all three cards and observations?
        self._num_of_cards = num_of_cards
        self._action_spec = array_spec.BoundedArraySpec(shape=(1,), dtype=np.int32, 
                                                        minimum=0, 
                                                        maximum=num_of_cards - 1, 
                                                        name='action')

        self._observation_spec = array_spec.BoundedArraySpec(shape=(num_of_cards,), dtype=np.int32, 
                                                             minimum=0, name='observation')
       
        self._reset_game()       
        

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset_game(self):
        self._state = np.zeros((self._num_of_cards,), dtype=np.int32)
        self._tries = 0
        self._solution = np.random.randint(0, 6)
        self._episode_ended = False

    def _reset(self):        
        self._reset_game()
        return ts.restart(self._state)

    def _step(self, action):
        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        self._tries += 1
        
        action = action[0]
        
        # Make sure episodes don't go on forever.
        if action >= 0 and action < self._num_of_cards:
            correct = self._guess(action)
        else:
            raise ValueError('`action` should be between 0 and ' + str(self._num_of_cards))

        if self._episode_ended or correct or self._tries == 10:
            reward = 10 - self._tries
            return ts.termination(self._state, reward)
        else:
            return ts.transition(self._state, reward=0.0, discount=1.0)

    def _handle_guess(self):
        pass

    def _guess(self, action) -> bool:
        self._state[action] += 1

        return action == self._solution


if __name__ == "__main__":
    environment = ClueCardCategoryEnv()
    utils.validate_py_environment(environment, episodes=5)




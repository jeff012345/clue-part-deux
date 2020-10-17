import tensorflow as tf
import numpy as np

import Clue

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

    _max_tries: int

    _num_of_cards: int

    _solution: int
    _tries: int

    game: Clue.Director
    
    def __init__(self, num_of_cards = 6):
        self._num_of_cards = num_of_cards
        self._max_tries = 5 * 5 * 8
        self._action_spec = array_spec.BoundedArraySpec(shape=(1,), 
                                                        dtype=np.int32, 
                                                        minimum=0, 
                                                        maximum=self._num_of_cards - 1, 
                                                        name='action')

        self._observation_spec = array_spec.BoundedArraySpec(shape=(self._num_of_cards,), 
                                                             dtype=np.int32, 
                                                             minimum=0, 
                                                             name='observation')
       
        self._reset_game()
        

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset_game(self):
        self._state = np.zeros((self._num_of_cards,), dtype=np.int32)
        self._tries = 0
        self._solution = np.random.randint(0, self._num_of_cards)
        self._episode_ended = False

    def _new_game(self):
        end_game_lock = Lock()
        director = Director(end_game_lock)

        players = [
		    ComputerPlayer(director),
		    ComputerPlayer(director),
		    ComputerPlayer(director),
		    ComputerPlayer(director),
		    ComputerPlayer(director),
		    ComputerPlayer(director)
	    ]

        director.new_game();

    def _reset(self):        
        self._reset_game()
        return ts.restart(self._state)

    def _step(self, action):
        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        self._tries += 1
                
        correct = self._guess(action)

        # Make sure episodes don't go on forever.
        if self._episode_ended or correct or self._tries == self._max_tries:
            reward = self._tries - self._num_of_cards \
                if self._tries <= self._num_of_cards else -1 * self._num_of_cards
            self._episode_ended = True
            return ts.termination(self._state, reward)
        else:
            return ts.transition(self._state, reward=0.0, discount=1.0)


    def _guess(self, action) -> bool:
        action = action[0]
        self._state[action] = 1

        return action == self._solution


if __name__ == "__main__":
    environment = ClueCardCategoryEnv()
    utils.validate_py_environment(environment, episodes=5)




from typing import List


import tensorflow as tf
import numpy as np
import math

from Clue import Director, GameStatus, GameEvent, GuessEvent
from player import Player, ComputerPlayer, PlayerAction
from ai_players import RLPlayerTrainer, RLPlayer
from definitions import CardType, Card, Weapon, Character
from stat_tracker import StatTracker

from threading import Lock

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.trajectories import time_step as ts

tf.compat.v1.enable_v2_behavior()
tf.keras.backend.set_floatx('float64')

class ClueGameEnv(py_environment.PyEnvironment):

    _max_tries: int
    _num_of_cards: int
    _tries: int
    _players: List[Player]
    _clue: Director
    _ai_player: Player
    _stat_tracker: StatTracker
    
    def __init__(self, eval = False):
        self._num_of_cards = 6 + 6
        self._num_of_combos = 6 * 6

        self._max_tries = self._num_of_combos * 2

        self._action_spec = array_spec.BoundedArraySpec(shape=(1,), 
                                                        dtype=np.int32, 
                                                        minimum=0, 
                                                        maximum=self._num_of_combos - 1, 
                                                        name='action')

        obv_cnt = self._num_of_cards + StatTracker.VALUE_COUNT        
        self._observation_spec = array_spec.BoundedArraySpec(shape=(obv_cnt,), 
                                                             dtype=np.float64, 
                                                             minimum=0, 
                                                             name='observation')
       
        self.__init_clue__(eval)
        self._reset()

    def __init_clue__(self, eval):
        if eval:
            self._ai_player = RLPlayer()
        else:
            self._ai_player = RLPlayerTrainer()

        self._players = [
		    ComputerPlayer(),
		    ComputerPlayer(),
		    ComputerPlayer(),
		    ComputerPlayer(),
		    ComputerPlayer(),
		    self._ai_player
	    ]

        end_game_lock = Lock()
        self._clue = Director(end_game_lock, self._players)
        self._clue.register(GameEvent.GUESS, self._handle_guess_event)
        print("Clue initialized!")

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        #print("new game!")        
        self._tries = 0
        self._episode_ended = False
        self._stat_tracker = StatTracker(len(self._players))

        self._clue.new_game()

        self._update_state()

        return ts.restart(self._state)

    def _update_state(self):
        arrs = (
            self._ai_player.log_book.weapons, \
            self._ai_player.log_book.characters, \
            self._stat_tracker.stat_array() \
        )
        self._state = np.concatenate(arrs, axis=None)

    def _step(self, action):
        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()               

        # take turns until the AI player needs to guess
        self._take_turns_until_guess()
        
        if self._clue.game_status == GameStatus.ENDED:
            # someone won, terminate
            self._episode_ended = True            
            return ts.termination(self._state, self._calc_reward())
        
        # make a guess        
        self._guess(action[0])

        self._update_state()

        if self._tries == self._max_tries:
            raise Exception("game took too long")

        return ts.transition(self._state, reward=0.0, discount=1.0)

    # max reward = -1 * num_of_cards
    def _calc_reward(self) -> int:
        if self._clue.winner == self._ai_player:
            # AI player won
            return -1 * self._tries
            
        # AI player lost the game, make this worse
        return -2 * self._max_tries

    def _take_turns_until_guess(self):
        player_action = None
        while player_action is None:
            # other players take a turn
            self._clue.take_turns_until_player(self._ai_player)

            if self._clue.game_status == GameStatus.ENDED:
                # another player has won
                #print("another player won")
                break

            player_action = self._ai_player.next_turn_action()

            if player_action == PlayerAction.GUESS:
                break

            # take the AI player turn
            self._clue.player_take_turn(self._ai_player)
            player_action = None

            if self._clue.game_status == GameStatus.ENDED:
                # AI player won
                #print("AI player won")
                break

    def _guess(self, action):
        self._tries += 1

        character_ordinal = (math.floor(action / 6) % 6) + 1
        weapon_ordinal = (action % 6) + 1

        self._ai_player.weapon_guess = Card(Weapon(weapon_ordinal), CardType.WEAPON)
        self._ai_player.character_guess = Card(Character(character_ordinal), CardType.CHARACTER)
        self._ai_player.make_guess()
        self._clue.next_player()

    def _handle_guess_event(self, event: GuessEvent):
        if event.player != self._ai_player:
            self._stat_tracker.log_guess(event.solution, event.skipped_players)

if __name__ == "__main__":
    environment = ClueCardCategoryEnv()
    utils.validate_py_environment(environment, episodes=5)




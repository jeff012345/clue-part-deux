from typing import List


import tensorflow as tf
import numpy as np
import math
import collections

from Clue import Director, GameStatus, GameEvent, GuessEvent
from player import Player, NaiveComputerPlayer, PlayerAction
from ai_players import RLPlayerRoomTrainer, RLPlayer
from definitions import CardType, Card, Weapon, Character, Room, RoomPosition
from stat_tracker import RoomTracker, CardStat
from paths import Board

from threading import Lock, Semaphore

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.trajectories import time_step as ts

tf.compat.v1.enable_v2_behavior()
#tf.keras.backend.set_floatx('float64')

class ClueGameRoomEnv(py_environment.PyEnvironment):

    _max_tries: int
    _num_of_cards: int
    _tries: int
    _players: List[Player]
    _clue: Director
    _ai_player: RLPlayer
    _stat_tracker: RoomTracker   

    def __init__(self, eval = False, director = None):
        self._num_of_cards = 9
        self._num_of_actions = self._num_of_cards

        self._max_tries = 40

        self._action_spec = array_spec.BoundedArraySpec(shape=(), 
                                                        dtype=np.int32, 
                                                        minimum=0, 
                                                        maximum=self._num_of_actions - 1, 
                                                        name='action')

        # knowns  = 9
        # card stats = 9 * 2
        # room_distance = 9
        obv_cnt = self._num_of_cards * 2 + self._num_of_cards * CardStat.COUNT
        self._observation_spec = array_spec.BoundedArraySpec(shape=(obv_cnt,), 
                                                             dtype=np.float64, 
                                                             minimum=0, 
                                                             name='observation')
        Board.calculate_room_distances()
        self.__init_clue__(eval, director)

    def __init_clue__(self, eval, director):
        if director is not None:
            # initialize from a existing clue director instance
            self._clue = director
            self._players = self._clue.players
            self._ai_player = next(p for p in self._players if isinstance(p, RLPlayer))
        else:
            if eval:
                self._ai_player = RLPlayer()
            else:
                self._ai_player = RLPlayerRoomTrainer()

            self._players = [
		        NaiveComputerPlayer(),
		        NaiveComputerPlayer(),
		        NaiveComputerPlayer(),
		        NaiveComputerPlayer(),
		        NaiveComputerPlayer(),
		        self._ai_player
	        ]

            end_game_lock = Lock()
            self._clue = Director(end_game_lock, self._players)

        # for the stat tracker
        self._clue.register(GameEvent.GUESS, self._handle_guess_event)

        print("Clue Room initialized!")

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        # Game Status = ???        
        self._tries = 0
        self._episode_ended = False
        self._stat_tracker = RoomTracker(len(self._players))

        self._clue.new_game()
        self._update_state()

        self._clue.game_status = GameStatus.RUNNING

        return ts.restart(self._state)

    def _update_state(self):
        arrs = (
            self._ai_player.log_book.rooms, \
            self._stat_tracker.stat_array(), \
            self._room_distances()
        )
        self._state = np.concatenate(arrs, axis=None)#.astype(np.float64)

    def _room_distances(self) -> List[np.float64]:
        p = self._ai_player.position
        if p is None:
            p = Board.ROOM_POSITIONS[self._ai_player.room]
        else:
            p = Board.get(p[0], p[1])

        return Board.ROOM_DISTANCES[p]

    def _step(self, action):
        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()               

        # take turns until the AI player needs take its turn
        self._clue.take_turns_until_player(self._ai_player)
        
        if self._clue.game_status == GameStatus.ENDED:
            # someone won, terminate
            self._episode_ended = True
            return ts.termination(self._state, self._calc_reward())
        
        #self._guess(action)
        self._turn(action)

        #TODO this state doesn't update after an action
        self._update_state()

        if self._clue.game_status == GameStatus.ENDED or self._tries == self._max_tries:
            # AI player won
            #print("AI Player Won!")
            self._episode_ended = True
            return ts.termination(self._state, self._calc_reward())

        return ts.transition(self._state, reward=0.0, discount=1.0)

    # max reward = -1 * num_of_cards
    def _calc_reward(self) -> int:
        #if self._tries == self._max_tries:
        #    return -90

        if self._clue.winner == self._ai_player:
            # the AI won
            return 0

        rooms_in_hand = len(self._ai_player.hand.rooms)
        reward = ((np.sum(self._ai_player.log_book.rooms) - rooms_in_hand) / (9 - rooms_in_hand)) - 1
        return int(reward) * 100

        # original
        #if self._clue.winner == self._ai_player:
        #    # AI player won
        #    return -1 * self._tries
            
        ## AI player lost the game, make this worse
        #return -1 * self._max_tries

        #if self._clue.winner == self._ai_player:
        #    # AI player won
        #    return 1

        #eliminated = np.sum(self._ai_player.log_book.rooms)
        #return eliminated / self._tries

    def _set_room(self, action):        
        self._ai_player.room_guess = Card(Room(action + 1), CardType.ROOM)

    def _turn(self, action):
        self._tries += 1
        self._set_room(action)
        self._ai_player.take_turn()
        self._clue.next_player()

    def _handle_guess_event(self, event: GuessEvent):
        if event.player != self._ai_player:
            self._stat_tracker.log_guess(event.solution, event.skipped_players)

class ClueGameRoomEnvImplementation(ClueGameRoomEnv):

    _ai_step_lock: Semaphore

    def __init__(self, ai_step_lock: Lock, director: Director):
        super().__init__(director=director)
        self._ai_step_lock = ai_step_lock

    # override
    def _reset(self):
        # Game Status = ???        
        self._stat_tracker = RoomTracker(len(self._players))
        self._update_state()
        return ts.restart(self._state)

    #Overrride
    def _step(self, action):
        self._set_room(action)
        print("room guess set: " + str(self._ai_player.room_guess))
        
        self._ai_step_lock.release()

        while not self._ai_step_lock.locked():
            # wait for other thread to get the lock
            pass

        self._ai_step_lock.acquire()
        
        # turn is over
        self._update_state()
        print("room env state updated")

        return ts.transition(self._state, reward=0.0, discount=1.0)

def main():
    environment = ClueGameRoomEnv()
    utils.validate_py_environment(environment, episodes=5)

if __name__ == "__main__":
    main()




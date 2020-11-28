from typing import List
import os
import time
from threading import Semaphore, Lock, Barrier

from player import NaiveComputerPlayer
from definitions import Card, Room, CardType, Character

import tensorflow as tf
from tf_agents.trajectories import time_step as ts

tf.compat.v1.enable_v2_behavior()

class RLPlayer(NaiveComputerPlayer):	
		
	weapon_guess: Card
	character_guess: Card
	room_guess: Card

	def __init__(self):
		super().__init__()
		self.weapon_guess = None
		self.character_guess = None
		self.room_guess = None

	# override
	def __repr__(self):
		return "RLPlayer: "  + str(self.character)

	def decide_character_guess(self) -> Card:
		if self.character_guess is None:
			return super().decide_character_guess()

		temp = self.character_guess
		self.character_guess = None
		return temp

	def decide_weapon_guess(self) -> Card:
		if self.weapon_guess is None:
			return super().decide_weapon_guess()

		temp = self.weapon_guess
		self.weapon_guess = None
		return temp

	def should_guess_current_room(self) -> bool:
		if self.room_guess is None:
			return super().should_guess_current_room()

		return self.room == self.room_guess.value

	def _get_unknown_rooms(self) -> List[Room]:
		if self.room_guess is None:
			return super()._get_unknown_rooms()

		return [self.room_guess.value]

class RLPlayerTrainer(RLPlayer):

	def should_guess_current_room(self) -> bool:
		return self.room == self.director.solution.room.value

	def _get_unknown_rooms(self) -> List[Room]:
		return [self.director.solution.room.value]

	# override
	def __repr__(self):
		return "RLPlayerTrainer: " + str(self.character)

class RLPlayerRoomTrainer(RLPlayer):

	def decide_character_guess(self) -> Card:
		return self.director.solution.character

	def decide_weapon_guess(self) -> Card:
		return self.director.solution.weapon

	# override
	def __repr__(self):
		return "RLPlayerRoomTrainer: " + str(self.character)


class DuelAiPlayer(RLPlayer):

	def __init__(self, set_guess_barrier: Barrier, next_turn_barrier: Barrier):
		super().__init__()

		self._set_guess_barrier = set_guess_barrier
		self._next_turn_barrier = next_turn_barrier

	# override
	def __repr__(self):
		return "DuelAiPlayer: " + str(self.character)

	# override
	def take_turn(self):
		if self.remaining_path is not None:
			super().take_turn()
			return

		self._next_turn_barrier.wait()
		self._next_turn_barrier.reset()

		self._set_guess_barrier.wait()

		super().take_turn()





		

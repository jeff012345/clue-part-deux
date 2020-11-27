from typing import List
import os
import time
from threading import Semaphore, Lock

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

class RLPlayerRoomTrainer(RLPlayer):

	def decide_character_guess(self) -> Card:
		return self.director.solution.character

	def decide_weapon_guess(self) -> Card:
		return self.director.solution.weapon


class DuelAiPlayer(RLPlayer):

	def __init__(self, guess_step_lock: Lock, room_step_lock: Lock):
		super().__init__()

		self._guess_step_lock = guess_step_lock
		self._room_step_lock = room_step_lock

	# override
	def take_turn(self):
		if self.remaining_path is not None:
			super().take_turn()
			return

		print("starting ai turn")

		# starting turn
		# release to update the guesses
		self._guess_step_lock.release()
		self._room_step_lock.release()

		while not self._guess_step_lock.locked() or not self._room_step_lock.locked(): 
			# wait for other thread to get the lock
			pass

		print("waiting for guesses to be updated")

		# wait for guesses to be updated
		self._guess_step_lock.acquire() 
		self._room_step_lock.acquire()

		print("ai taking turn")

		super().take_turn()

		print("ai turn done")


	# overrride
	#def make_guess(self):
		
		#super().make_guess()

		

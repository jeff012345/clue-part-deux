from typing import List

import os
from player import ComputerPlayer
from definitions import Card, Room, CardType, Character

import tensorflow as tf
from tf_agents.trajectories import time_step as ts

tf.compat.v1.enable_v2_behavior()

class RLPlayer(ComputerPlayer):	
		
	weapon_guess: Card
	character_guess: Card

	def __init__(self):
		super().__init__()
		self.weapon_guess = None
		self.character_guess = None

	def decide_character_guess(self) -> Card:
		if self.character_guess is None:
			raise Exception("No character guess set")

		temp = self.character_guess
		self.character_guess = None
		return temp

	def decide_weapon_guess(self) -> Card:
		if self.weapon_guess is None:
			raise Exception("No weapon guess set")

		temp = self.weapon_guess
		self.weapon_guess = None
		return temp

class RLPlayerTrainer(RLPlayer):	

	def should_guess_current_room(self) -> bool:
		return self.room == self.director.solution.room.value

	def _get_unknown_rooms(self) -> List[Room]:
		return [self.director.solution.room.value]

	
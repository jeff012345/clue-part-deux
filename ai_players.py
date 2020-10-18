from typing import List

import os
from player import ComputerPlayer
from definitions import Card, Room, CardType

class RLPlayer(ComputerPlayer):	

	weapon_guess: Card

	def __init__(self):
		super().__init__()
		self.weapon_guess = None
		#policy_dir = os.path.join(".", 'policy')
		#self.saved_policy = tf.compat.v2.saved_model.load(policy_dir)

	def should_guess_current_room(self) -> bool:
		return self.room == self.director.solution.room.value
		#return super().should_guess_current_room()

	def decide_character_guess(self) -> Card:
		# pick the right character for training
		return self.director.solution.character

	def _get_unknown_rooms(self) -> List[Room]:
		return [self.director.solution.room.value]

	def decide_weapon_guess(self) -> Card:
		if self.weapon_guess is None:
			raise Exception("No weapon guess set")

		temp = self.weapon_guess
		self.weapon_guess = None
		return temp

	

	

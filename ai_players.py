from typing import List

import os
from player import ComputerPlayer
from definitions import Card, Room, CardType, Character

import tensorflow as tf
from tf_agents.trajectories import time_step as ts

tf.compat.v1.enable_v2_behavior()


class RLPlayerTrainer(ComputerPlayer):	

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

	
class RLPlayer(ComputerPlayer):	

	#_weapon_policy
	#_character_policy
	_weapon_policy_ts: ts.TimeStep
	_character_policy_ts: ts.TimeStep

	def __init__(self, weapon_policy, character_policy):
		super().__init__()
		
		policy_dir = os.path.join(".", weapon_policy)
		self._weapon_policy = tf.compat.v2.saved_model.load(policy_dir)

		policy_dir = os.path.join(".", character_policy)
		self._character_policy = tf.compat.v2.saved_model.load(policy_dir)

	def reset(self):
		super().reset()

		#self._weapon_policy_state = self._weapon_policy.get_initial_state(batch_size=1)
		#self._character_policy_state = self._character_policy.get_initial_state(batch_size=1)

		self._weapon_policy_ts = ts.restart(self.log_book.weapons)
		self._character_policy_ts = ts.restart(self.log_book.characters)

	def should_guess_current_room(self) -> bool:
		return super().should_guess_current_room()

	def decide_character_guess(self) -> Card:
		action_step = self._character_policy.action(self._character_policy_ts)
		
		character = Character(action_step.action[0] + 1)
		return Card(character, CardType.CHARACTER)

	def _get_unknown_rooms(self) -> List[Room]:
		return [self.director.solution.room.value]

	def decide_weapon_guess(self) -> Card:
		action_step = self._weapon_policy.action(self._weapon_policy_ts)
		
		weapon = Weapon(action_step.action[0] + 1)
		return Card(character, CardType.WEAPON)
	

	def _log_guess_match(self, guess, match, skipped_count):
		super()._log_guess_match(guess, match, skipped_count)

		self._weapon_policy_ts = ts.transition(self.log_book.weapons, reward=0.0, discount=1.0)
		self._character_policy_ts = ts.transition(self.log_book.characters, reward=0.0, discount=1.0)
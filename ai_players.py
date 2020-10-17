import os
from player import ComputerPlayer

class RLPlayer(ComputerPlayer):

	

	def __init__(self):
		policy_dir = os.path.join(".", 'policy')
		self.saved_policy = tf.compat.v2.saved_model.load(policy_dir)

	def decide_weapon_guess(self) -> Card:
		raise Exception('Not Implemented')

	def decide_character_guess(self) -> Card:
		raise Exception('Not Implemented')

	def should_guess_current_room(self) -> bool:
		raise Exception('Not Implemented')

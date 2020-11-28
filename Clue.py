from enum import Enum
from typing import List, Set, Dict, Tuple, Optional, Callable
import random
from paths import RoomPath, Board
from definitions import *
from player import *
from ai_players import RLPlayer
from threading import Lock
import time

class GameStatus(Enum):
	STARTING = 0
	INITIALIZED = 1
	READY = 2
	RUNNING = 3
	ENDED = 4

PLAYER_ORDER = [
	(Character.MISS_SCARLET, (1, 17)),
	(Character.COLONEL_MUSTARD, (8, 24)),
	(Character.MRS_WHITE, (25, 15)),
	(Character.MR_GREEN, (25, 10)),
	(Character.MRS_PEACOCK, (19, 1)),			
	(Character.PROFESSOR_PLUM, (6, 1))
]

PLAYER_ROTATION: Dict[Character, Character] = dict()
PLAYER_ROTATION[Character.MISS_SCARLET] = Character.COLONEL_MUSTARD
PLAYER_ROTATION[Character.COLONEL_MUSTARD] = Character.MRS_WHITE
PLAYER_ROTATION[Character.MRS_WHITE] = Character.MR_GREEN
PLAYER_ROTATION[Character.MR_GREEN] = Character.MRS_PEACOCK
PLAYER_ROTATION[Character.MRS_PEACOCK] = Character.PROFESSOR_PLUM
PLAYER_ROTATION[Character.PROFESSOR_PLUM] = Character.MISS_SCARLET

class GameEvent(Enum):
	GUESS = 1

class GuessEvent:
	player: Player
	solution: Solution
	skipped_players: int

	def __init__(self, player: Player, solution: Solution, skipped_players: int):
		self.player = player
		self.solution = solution
		self.skipped_players = skipped_players

class Director:
	
	## static
	def _pick_first(deck: List[Card], type: CardType) -> Card:
		i = 0
		for card in deck:
			if card.type == type:
				return deck.pop(i)
			i += 1
		
		return None

	players: List[Player]
	remaining_players: List[Player]
	player_by_character: Dict[Character, Player]
	solution: Solution
	winner: Player
	game_status: GameStatus
	end_game_lock: Lock
	_turn_lock: Lock
	_human_player: HumanPlayer
	_event_handlers: Dict[GameEvent, List[Callable]]
	active_player: Player	

	def __init__(self, end_game_lock: Lock, players: List[Player], turn_lock = None):
		self.game_status = GameStatus.STARTING
		self.player_by_character = dict()
		self._human_player = None

		self._turn_lock = turn_lock
		self.end_game_lock = end_game_lock
		self.players = players		

		for p in self.players:
			p.director = self

			if isinstance(p, HumanPlayer):
				self._human_player = p

		self._event_handlers = dict()
		for event in GameEvent:
			self._event_handlers[event] = []

	def register(self, event: GameEvent, func: Callable):
		self._event_handlers[event].append(func)

	def new_game(self):
		if self.game_status != GameStatus.STARTING and self.game_status != GameStatus.ENDED:
			raise Exception("new game called at the wrong time: Status = " + str(self.game_status))

		self.winner = None
		self.game_status = GameStatus.READY

		self._assign_players()	
		self._setup_cards()

		self.game_status = GameStatus.INITIALIZED

	def _setup_cards(self):
		deck = Deck.make_deck()
		random.shuffle(deck)

		self.solution = Solution(
			Director._pick_first(deck, CardType.WEAPON),
			Director._pick_first(deck, CardType.CHARACTER),
			Director._pick_first(deck, CardType.ROOM)		
		)

		self._deal_cards(deck)

	def play_auto_game(self):
		if self.game_status != GameStatus.INITIALIZED:
			raise Exception("Game not setup")

		self.game_status = GameStatus.RUNNING

		while not self._end_game():
			for player in self.remaining_players:
				player.take_turn()

				if self._end_game():
					return

		self.game_status = GameStatus.ENDED

	def play_auto_game_with_lock(self, end_game_lock: Lock):
		if self.game_status != GameStatus.INITIALIZED:
			raise Exception("Game not setup")

		self.game_status = GameStatus.RUNNING

		while not self._end_game():
			self.active_player.take_turn() 
			self.next_player()

		self.game_status = GameStatus.ENDED

		if self.winner != None and self._human_player is not None and self.winner != self._human_player:
			self._human_player.on_turn(GameOver(self.winner, self.solution))
			self._wait_for_user()

	def take_turns_until_player(self, stop_player: Player):
		if self._turn_lock is not None:
			self._take_turns_until_player_with_lock(stop_player)
			return

		while self.active_player != stop_player:
			self.player_take_turn(self.active_player)

			if self.game_status == GameStatus.ENDED:
				return

	def _take_turns_until_player_with_lock(self, stop_player: Player):
		while self.active_player != stop_player:
			if isinstance(self.active_player, HumanPlayer):
				human = self.active_player
				self.player_take_turn(human)
				
				self._wait_for_user()

				if human.player_action == PlayerAction.GUESS:
					(match, skipped, showing_player) = self.make_guess(human, human.solution)
					human.on_turn(GuessOutcome(match, showing_player))
					self._wait_for_user()

				elif human.player_action == PlayerAction.ACCUSATION:
					correct = self.make_accusation(human, human.solution)
					human.on_turn(AccusationOutcome(correct, human.solution))
					self._wait_for_user()
					
			else:
				self.player_take_turn(self.active_player)

			if self.game_status == GameStatus.ENDED:
				return

		if self.winner != None and self.winner != self._human_player:
			self._human_player.on_turn(GameOver(self.winner, self.solution))
			self._wait_for_user()

	def _wait_for_user(self):
		# wait for other thread to get it. probably not needed
		while not self._turn_lock.locked():
			pass

		self._turn_lock.acquire()
		self._turn_lock.release()

	def player_take_turn(self, player: Player):		
		player.take_turn()

		if self._end_game():
			self.game_status = GameStatus.ENDED
			return

		self.next_player()

	def next_player(self):
		next_character = PLAYER_ROTATION[self.active_player.character]
		self.active_player = self.player_by_character[next_character]

	def _deal_cards(self, deck):
		i = 0
		num_of_players = len(self.players)

		for card in deck:
			self.players[i].give_card(card)
			i += 1

			if i == num_of_players:
				i = 0

		if self._human_player is not None:
			self._human_player.on_turn(DealCard(self._human_player.hand.all))
			self._wait_for_user()

	def _assign_players(self):
		for p in self.players:
			p.reset()

		random.shuffle(self.players)
		self.remaining_players = self.players.copy()
				
		self.player_by_character.clear()

		i = 0
		for player in self.players:
			player.character = PLAYER_ORDER[i][0]

			self.player_by_character[player.character] = player

			# assign start location
			start = PLAYER_ORDER[i][1]
			pos = Board.get(start[0] - 1, start[1] - 1)
			player.move(pos)
			#player.position = (start[0] - 1, start[1] - 1)

			i += 1
			
		self.active_player = self.players[0]

	## store the order somewhere so it doesn't need to be calculated each time
	def make_guess(self, player: Player, solution: Solution) -> Tuple[Solution, int, Player]:
		if not solution.is_complete():
			print('Incomplete guess')
			print(solution)
			print(player.log_book.log_book)
			raise Exception()

		if self._human_player is not None and player != self._human_player:
			self._human_player.on_turn(OpponentGuess(player, solution))
			self._wait_for_user()

		## move the accused player
		# removed for training
		#try:
		#	self.player_by_character[solution.character.value].enter_room(solution.room.value)
		#except KeyError as err:
		#	print(self.player_by_character)
		#	raise err

		## ask each player in order
		skipped_players = 0
		for other_player in self._asking_order(player):
			if isinstance(other_player, HumanPlayer):
				match = other_player.show_card(solution)

				if match is not None:
					# wait for other thread to get it. probably not needed
					while not self._turn_lock.locked():
						pass

					self._turn_lock.acquire()
					self._turn_lock.release()
			else:
				match = other_player.show_card(solution)

			if match is not None:
				self._on_guess(player, solution, skipped_players)
				return (match, skipped_players, other_player)

			skipped_players += 1

		self._on_guess(player, solution, skipped_players)
		return (None, skipped_players, None)

	def _on_guess(self, player: Player, solution: Solution, skipped_players: int):
		event = GuessEvent(player, solution, skipped_players)
		for func in self._event_handlers[GameEvent.GUESS]:
			func(event)	

	def _asking_order(self, player: Player) -> List[Player]:
		player_index = self.players.index(player)

		## determine the order to ask each player (clockwise around the board)
		if player_index == 0:
			# first player
			return self.players[1:]
		elif player_index == len(self.players) - 1:
			# last player
			return self.players[:-1]
		else:
			return self.players[player_index+1:] + self.players[0:player_index]

	def make_accusation(self, player: Player, solution: Solution) -> bool:
		#print(str(player.character) + " is making an accusation")
		#print(solution)

		if self.solution.is_match(solution):
			self.winner = player
			self.game_status = GameStatus.ENDED
			return True
		else:
			## player loses and doesn't get any more turns
			self.remaining_players.remove(player)
			print('this shouldn\'t happen')

			if isinstance(player, HumanPlayer):
				self.game_status = GameStatus.ENDED
				return False
			raise Exception()
	
	def _end_game(self):
		## no winner and at least 2 players
		return self.game_status == GameStatus.ENDED or self.winner is not None \
		   or len(self.players) == 1 or self.end_game_lock.locked() is True

def new_game(director: Director):
	director.new_game();
	#print("Solution")
	#print(director.solution)


def main():
	sum = 0
	cnt = 0

	#ai_player = RLPlayer(weapon_policy = "policy_PoE-1", 
	#				  character_policy = "policy_PoE-1")

	ai_player = RLPlayer()	

	players = [
		NaiveComputerPlayer(),
		NaiveComputerPlayer(),
		NaiveComputerPlayer(),
		NaiveComputerPlayer(),
		NaiveComputerPlayer(),
		ai_player
	]

	end_game_lock = Lock()
	director = Director(end_game_lock, players)	

	while cnt <= 100:
		start = time.perf_counter()
		director.new_game()
		director.play_auto_game();
		end = time.perf_counter()

		sum += end - start
		cnt += 1

		if cnt % 100 == 0:
			print("Average Time per game = " + str(sum / cnt) +"; Total Games = " + str(cnt))

def asfdlkjasf():

	eval_py_env = ClueGameEnv(eval = True)
	eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)

	policy_dir = os.path.join("policy-reinforce")
	saved_policy = tf.compat.v2.saved_model.load(policy_dir)

	num_episodes = 3
	for _ in range(num_episodes):
		time_step = eval_tf_env.reset()

		while not time_step.is_last():
			action_step = saved_policy.action(time_step)
			time_step = eval_tf_env.step(action_step.action)

		if eval_py_env._clue.winner == eval_py_env._ai_player:
			wins += 1


if __name__ == "__main__":
	#main()
	asfdlkjasf()
import threading
import sys
import os
import traceback

import game_board
import Clue
from player import NaiveComputerPlayer, HumanPlayer
from ai_players import RLPlayer
from clue_tf_env import ClueGameEnv

run_game_lock = threading.Lock()
end_game_lock = threading.Lock()
turn_lock = threading.Lock()

human_player = HumanPlayer()

players = [
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	human_player,
	RLPlayer()
]

director = Clue.Director(end_game_lock, players, turn_lock)

# runs the UI game board
def run_board():    
    try:
        run_game_lock.acquire()
        game_board.run(director, run_game_lock, end_game_lock, human_player, turn_lock)
    except Exception as err:
        end_game_lock.acquire()

        traceback.print_tb(err.__traceback__)
        raise err

# runs the game director and TF agent
def run_game():    
    import tensorflow as tf
    from tf_agents.environments import tf_py_environment
    from tf_agents.policies import policy_saver

    tf.compat.v1.enable_v2_behavior()

    eval_py_env = ClueGameEnv(director = director)
    eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)

    policy_dir = os.path.join("policy-reinforce")
    saved_policy = tf.compat.v2.saved_model.load(policy_dir)

    try:
        time_step = eval_tf_env.reset()

        run_game_lock.acquire()

        while not end_game_lock.locked() and not time_step.is_last():            
            action_step = saved_policy.action(time_step)
            time_step = eval_tf_env.step(action_step.action)
            
        run_game_lock.release()

        #game is done
        if not end_game_lock.locked():
            end_game_lock.acquire()

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()

        traceback.print_tb(err.__traceback__)
        raise err

if __name__ == "__main__":
    thread1 = threading.Thread(target=run_board)
    thread2 = threading.Thread(target=run_game)

    # Will execute both in parallel
    thread1.start()
    thread2.start()

    # Joins threads back to the parent process, which is this program
    thread1.join()
    thread2.join()

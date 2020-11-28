import threading
import sys
import os
import traceback

import game_board
from Clue import Director
from player import NaiveComputerPlayer, HumanPlayer
from ai_players import RLPlayer, DuelAiPlayer
from paths import Board

## Model Config
room_policy_dir = os.path.join("models_no_delete", "room", "cat dqn-1 more", "policy")
guess_policy_dir = os.path.join("models_no_delete", "best_guess_policy")

## setup
new_game_barrier = threading.Barrier(3)
set_guess_barrier = threading.Barrier(3)
next_turn_barrier = threading.Barrier(3)

end_game_lock = threading.Lock()
run_game_lock = threading.Lock()
run_game_lock.acquire()

interaction_lock = threading.Lock()

human_player = HumanPlayer(interaction_lock)
ai_player = DuelAiPlayer(set_guess_barrier, next_turn_barrier)

players = [
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	human_player,
	ai_player
]

director = Director(end_game_lock, players, interaction_lock)

def load_room_env():
    import tensorflow as tf     
    from tf_agents.environments import tf_py_environment
    from tf_agents.policies import policy_saver

    from clue_room_tf_env import ClueGameRoomEnvImplementation
    
    tf.compat.v1.enable_v2_behavior()

    eval_py_env = ClueGameRoomEnvImplementation(director, set_guess_barrier, next_turn_barrier)
    eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)

    saved_policy = tf.compat.v2.saved_model.load(room_policy_dir)

    return (eval_tf_env, saved_policy)

def load_guess_env():
    import tensorflow as tf     
    from tf_agents.environments import tf_py_environment
    from tf_agents.policies import policy_saver

    from clue_tf_env import ClueGameEnvImplementation

    tf.compat.v1.enable_v2_behavior()

    eval_py_env = ClueGameEnvImplementation(director, set_guess_barrier, next_turn_barrier)
    eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)
    
    saved_policy = tf.compat.v2.saved_model.load(guess_policy_dir)

    return (eval_tf_env, saved_policy)

# THREAD: runs the UI game board
def run_board():    
    try:        
        game_board.run(director, run_game_lock, end_game_lock, human_player, interaction_lock)
    except Exception as err:
        end_game_lock.acquire()

        traceback.print_tb(err.__traceback__)
        raise err

# THREAD: runs the game director
def run_game():
    try:
        Board.calculate_room_distances()

        # wait for player to start the game
        run_game_lock.acquire()

        if end_game_lock.locked():
            # player quit game before start
            new_game_barrier.abort()
            return

        director.new_game()

        # signal this thread is ready to start
        new_game_barrier.wait()

        director.play_auto_game_with_lock(end_game_lock)

        #game is done
        if not end_game_lock.locked():
            end_game_lock.acquire()

        # signal env threads to quit
        next_turn_barrier.abort()

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()

        new_game_barrier.abort()
        set_guess_barrier.abort()
        next_turn_barrier.abort()
            
        traceback.print_tb(err.__traceback__)
        raise err

# THREAD: runs the weapon and character guess TF environment
def run_guess_ai():
    try:
        (guess_env, guess_policy) = load_guess_env()

        # signal this thread is ready to start
        new_game_barrier.wait()

        # wait for first turn
        next_turn_barrier.wait()

        guess_time_step = guess_env.reset()

        while not end_game_lock.locked():
            # set the guess and wait for next turn
            guess_action_step = guess_policy.action(guess_time_step)
            guess_time_step = guess_env.step(guess_action_step.action)
    
    except threading.BrokenBarrierError as err:
        print("barrier was aborted. Quiting...")

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()

        new_game_barrier.abort()
        next_turn_barrier.abort()
        set_guess_barrier.abort()

        traceback.print_tb(err.__traceback__)
        raise err

# THREAD: runs the room guess TF environment
def run_room_ai():
    try:
        (room_env, room_policy) = load_room_env()

        # signal this thread is ready to start
        new_game_barrier.wait()

        # wait for first turn
        next_turn_barrier.wait()

        room_time_step = room_env.reset()

        while not end_game_lock.locked():
            # set the guess and wait for next turn
            room_action_step = room_policy.action(room_time_step)
            room_time_step = room_env.step(room_action_step.action)

    except threading.BrokenBarrierError as err:
        print("barrier was aborted. Quiting...")

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()

        new_game_barrier.abort()
        next_turn_barrier.abort()
        set_guess_barrier.abort()

        traceback.print_tb(err.__traceback__)
        raise err

if __name__ == "__main__":
    thread1 = threading.Thread(target=run_board)
    thread2 = threading.Thread(target=run_game)
    thread3 = threading.Thread(target=run_room_ai)
    thread4 = threading.Thread(target=run_guess_ai)

    # Will execute both in parallel
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    # Joins threads back to the parent process, which is this program
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
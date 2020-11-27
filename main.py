import threading
import sys
import os
import traceback

import game_board
from Clue import Director
from player import NaiveComputerPlayer, HumanPlayer
from ai_players import RLPlayer, DuelAiPlayer
from paths import Board

def load_room_env(director: Director, ai_step_lock: threading.Semaphore):
    import tensorflow as tf     
    from tf_agents.environments import tf_py_environment
    from tf_agents.policies import policy_saver

    from clue_room_tf_env import ClueGameRoomEnvImplementation
    
    tf.compat.v1.enable_v2_behavior()

    eval_py_env = ClueGameRoomEnvImplementation(ai_step_lock, director)
    eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)

    policy_dir = os.path.join("models_no_delete", "room", "cat dqn-1 more", "policy")
    saved_policy = tf.compat.v2.saved_model.load(policy_dir)

    return (eval_tf_env, saved_policy)

def load_guess_env(director: Director, ai_step_lock: threading.Semaphore):
    import tensorflow as tf     
    from tf_agents.environments import tf_py_environment
    from tf_agents.policies import policy_saver

    from clue_tf_env import ClueGameEnvImplementation

    tf.compat.v1.enable_v2_behavior()

    eval_py_env = ClueGameEnvImplementation(ai_step_lock, director)
    eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)

    policy_dir = os.path.join("models_no_delete", "best_guess_policy")
    saved_policy = tf.compat.v2.saved_model.load(policy_dir)

    return (eval_tf_env, saved_policy)

director_ready = threading.Barrier(3)

end_game_lock = threading.Lock()
run_game_lock = threading.Lock()
run_game_lock.acquire()

turn_lock = threading.Lock()
guess_step_lock = threading.Lock()
room_step_lock = threading.Lock()

human_player = HumanPlayer(turn_lock)
ai_player = DuelAiPlayer(guess_step_lock, room_step_lock)

players = [
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	human_player,
	ai_player
]

director = Director(end_game_lock, players, turn_lock)

# runs the UI game board
def run_board():    
    try:        
        game_board.run(director, run_game_lock, end_game_lock, human_player, turn_lock)
    except Exception as err:
        end_game_lock.acquire()

        traceback.print_tb(err.__traceback__)
        raise err

# runs the game director and TF agent
def run_game():    
    try:
        # wait for player to start the game
        run_game_lock.acquire()

        if end_game_lock.locked():
            # player quit game before start
            director_ready.wait()
            return

        director.new_game()

        guess_step_lock.acquire()
        room_step_lock.acquire()        

        director_ready.wait()

        director.play_auto_game_with_lock(end_game_lock)

        #game is done
        if not end_game_lock.locked():
            end_game_lock.acquire()

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()

        if director_ready.n_waiting > 0:
            director_ready.wait()

        if guess_step_lock.locked():
            guess_step_lock.release()

        if room_step_lock.locked():
            room_step_lock.release()

        traceback.print_tb(err.__traceback__)
        raise err

    # close the ai thread
    if guess_step_lock.locked():
        guess_step_lock.release()

    if room_step_lock.locked():
        room_step_lock.release()

def run_guess_ai():
    (guess_env, guess_policy) = load_guess_env(director, guess_step_lock)

    print("guess director wait")
    director_ready.wait()
    print("guess director wait - complete")

    if end_game_lock.locked():        
        # player quit game before start
        return 

    guess_time_step = guess_env.reset()   
    print("guess env reset") 
        
    guess_step_lock.acquire()
    print("starting guess ai")    

    try:
        while not end_game_lock.locked():
            guess_action_step = guess_policy.action(guess_time_step)
            guess_time_step = guess_env.step(guess_action_step.action)

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()


        traceback.print_tb(err.__traceback__)
        raise err

def run_room_ai():
    (room_env, room_policy) = load_room_env(director, room_step_lock)

    print("room director wait")
    director_ready.wait()
    print("room director wait - complete")

    if end_game_lock.locked():
        # player quit game before start
        return

    room_time_step = room_env.reset()
    print("room env reset")
    
    room_step_lock.acquire()
    print("starting room ai")

    try:
        while not end_game_lock.locked():
            room_action_step = room_policy.action(room_time_step)
            room_time_step = room_env.step(room_action_step.action)

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()

        traceback.print_tb(err.__traceback__)
        raise err

if __name__ == "__main__":
    thread1 = threading.Thread(target=run_board)
    thread2 = threading.Thread(target=run_game)
    thread3 = threading.Thread(target=run_room_ai)
    thread4 = threading.Thread(target=run_guess_ai)
    thread5 = threading.Thread(target=Board.calculate_room_distances)

    # Will execute both in parallel
    thread5.start()
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    # Joins threads back to the parent process, which is this program
    thread5.join()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
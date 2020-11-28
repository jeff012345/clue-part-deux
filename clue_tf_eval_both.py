import threading
import sys
import os
import traceback

import game_board
from Clue import Director
from player import NaiveComputerPlayer, HumanPlayer
from ai_players import RLPlayer, DuelAiPlayer
from paths import Board

new_game_barrier = threading.Barrier(3)

end_game_lock = threading.Lock()

set_guess_barrier = threading.Barrier(3)
next_turn_barrier = threading.Barrier(3)

end_evaluation = threading.Lock()

ai_player = DuelAiPlayer(set_guess_barrier, next_turn_barrier)

players = [
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	NaiveComputerPlayer(),
	ai_player
]

director = Director(end_game_lock, players)

## Results
## Step = 5000; AI win ratio = 0.1878
## Final AI win ratio = 0.1878

def load_room_env():
    import tensorflow as tf     
    from tf_agents.environments import tf_py_environment
    from tf_agents.policies import policy_saver

    from clue_room_tf_env import ClueGameRoomEnvImplementation
    
    tf.compat.v1.enable_v2_behavior()

    eval_py_env = ClueGameRoomEnvImplementation(director, set_guess_barrier, next_turn_barrier)
    eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)

    policy_dir = os.path.join("models_no_delete", "room", "cat dqn-1 more", "policy")
    saved_policy = tf.compat.v2.saved_model.load(policy_dir)

    return (eval_tf_env, saved_policy)

def load_guess_env():
    import tensorflow as tf     
    from tf_agents.environments import tf_py_environment
    from tf_agents.policies import policy_saver

    from clue_tf_env import ClueGameEnvImplementation

    tf.compat.v1.enable_v2_behavior()

    eval_py_env = ClueGameEnvImplementation(director, set_guess_barrier, next_turn_barrier)
    eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)

    policy_dir = os.path.join("models_no_delete", "best_guess_policy")
    saved_policy = tf.compat.v2.saved_model.load(policy_dir)

    return (eval_tf_env, saved_policy)

# runs the game director and TF agent
def run_game():
    ### PARAMS
    num_of_games = 5000
    log_interval = 50

    try:
        end_game_lock.acquire()
        Board.calculate_room_distances()

        ai_wins = 0
        games_left = num_of_games

        while games_left > 0:
            set_guess_barrier.reset()
            next_turn_barrier.reset()
            
            director.new_game()
            new_game_barrier.wait()
            end_game_lock.release()
            
            director.play_auto_game_with_lock(end_game_lock)

            #print("AI Player = " + str(ai_player))
            #print("Winner = " + str(director.winner))

            if ai_player == director.winner:
                ai_wins += 1

            new_game_barrier.reset()
            end_game_lock.acquire()

            games_left -= 1

            if games_left == 0:
                print("evaluation end")
                end_evaluation.acquire()

            if games_left % log_interval == 0:
                games_played = num_of_games - games_left
                print("Step = " + str(games_played) + "; AI win ratio = " + str(ai_wins / games_played))

            # make the environment cycle
            next_turn_barrier.wait()

        print("Final AI win ratio = " + str(ai_wins / num_of_games))

    except Exception as err:
        if not end_evaluation.locked():
            end_evaluation.acquire()

        if not end_game_lock.locked():
            end_game_lock.acquire()

        new_game_barrier.abort()
        set_guess_barrier.abort()
        next_turn_barrier.abort()

        traceback.print_tb(err.__traceback__)
        raise err

def run_guess_ai():
    (guess_env, guess_policy) = load_guess_env()

    try:
        while not end_evaluation.locked():
            new_game_barrier.wait()                       
            next_turn_barrier.wait()

            guess_time_step = guess_env.reset()

            while not end_game_lock.locked():
                guess_action_step = guess_policy.action(guess_time_step)
                guess_time_step = guess_env.step(guess_action_step.action)

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()

        traceback.print_tb(err.__traceback__)
        raise err

def run_room_ai():
    (room_env, room_policy) = load_room_env()    

    try:
        while not end_evaluation.locked():
            new_game_barrier.wait()                       
            next_turn_barrier.wait()

            room_time_step = room_env.reset()

            while not end_game_lock.locked():
                room_action_step = room_policy.action(room_time_step)
                room_time_step = room_env.step(room_action_step.action)

    except Exception as err:
        if not end_game_lock.locked():
            end_game_lock.acquire()

        traceback.print_tb(err.__traceback__)
        raise err

if __name__ == "__main__":
    thread1 = threading.Thread(target=run_game)
    thread2 = threading.Thread(target=run_room_ai)
    thread3 = threading.Thread(target=run_guess_ai)

    # Will execute both in parallel
    thread1.start()
    thread2.start()
    thread3.start()

    # Joins threads back to the parent process, which is this program
    thread1.join()
    thread2.join()
    thread3.join()
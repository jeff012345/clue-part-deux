import threading
import sys
import traceback
import game_board
import Clue
from player import ComputerPlayer

run_game_lock = threading.Lock()
end_game_lock = threading.Lock()

director = Clue.Director(end_game_lock)

players = [
	ComputerPlayer(director),
	ComputerPlayer(director),
	ComputerPlayer(director),
	ComputerPlayer(director),
	ComputerPlayer(director),
	ComputerPlayer(director)
]

def run_board():
    try:
        run_game_lock.acquire()
        game_board.run(director, run_game_lock, end_game_lock)
    except Exception as err:
        end_game_lock.acquire()

        traceback.print_tb(err.__traceback__)
        raise err


def run_game():
    try:
        while not end_game_lock.locked():
            run_game_lock.acquire()
            Clue.new_game(director)
            run_game_lock.release()
    except Exception as err:
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

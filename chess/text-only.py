"""
main.py

Handles game state drawing and UI features: key handling, mouse handing, square highlighting, animations.

"""

#import pygame as p
from chess import engine, move_finder
from multiprocessing import Process, Queue
import time


"""

will clean this up eventually

"""


def main():
    #p.init()  # initialize py game

    #display = p.display.set_mode((width, height))  # set up game display
    #clock = p.time.Clock()
    #display.fill(p.Color("white"))
    #to_animate = False

    game_state = engine.GameState()  # initialize game state
    valid_moves = game_state.generate_valid_moves()  # generate valid moves
    move_made = False  # to check whether a move has been made since the last game state update

    #load_images()  # load images

    selected = ()  # track player selections
    player_selections = []

    white = False  # true if human is playing as white
    black = False
    move_undone = False
    move_finder_process = None
    ai_thinking = False

    white_time = 0
    black_time = 0
    w_turn = 0
    b_turn = 0

    start_time = 0
    final_time = 0

    running = True  # Default running state
    game_over = False
    while running:
        human = (game_state.white_to_move and white) or (not game_state.white_to_move and black)

        if not game_over and not human and not move_undone:
            if not ai_thinking:
                start_time = time.time()
                ai_thinking = True
                return_queue = Queue()  # used to pass data between threads
                move_finder_process = Process(target=move_finder.find_best_move, args=(game_state, valid_moves,
                                                                                       return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = move_finder.find_random_moves(valid_moves)
                game_state.make_move(ai_move)
                move_made = True
                ai_thinking = False
                final_time = time.time()
                if game_state.white_to_move:
                    white_time += (final_time - start_time)
                    w_turn+=1
                else:
                    black_time += (final_time - start_time)
                    b_turn+=1

        if move_made:
            print(game_state.move_log[-1].chess_notation())
            valid_moves = game_state.generate_valid_moves()
            move_made = False
            move_undone = False

        if game_state.is_checkmate():
            game_over = True
            if game_state.white_to_move:
                print("Black wins by checkmate!")
            else:
                print("White wins by checkmate!")
            print("avg white time = " + str(white_time/w_turn))
            print("avg black time = " + str(black_time/b_turn))
        elif game_state.is_stalemate():
            game_over = True
            print("Stalemate.")
            print("avg white time = " + str(white_time/w_turn))
            print("avg black time = " + str(black_time/b_turn))


    return 0


if __name__ == "__main__":
    main()

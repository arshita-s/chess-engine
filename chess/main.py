"""
main.py

Handles game state drawing and UI features: key handling, mouse handing, square highlighting, animations.

"""

import pygame as p
from chess import engine, move_finder
from multiprocessing import Process, Queue


# game window details
board_colors = [p.Color(255, 248, 220), p.Color(210, 180, 140)]

height = width = 512  # pixels
dim = 8  # Ranks and files
square_size = height // dim
fps = 5
images = {}

"""

will clean this up eventually

"""


def main():
    p.init()  # initialize py game

    display = p.display.set_mode((width, height))  # set up game display
    clock = p.time.Clock()
    display.fill(p.Color("white"))
    to_animate = False

    game_state = engine.GameState()  # initialize game state
    valid_moves = game_state.generate_valid_moves()  # generate valid moves
    move_made = False  # to check whether a move has been made since the last game state update

    load_images()  # load images

    selected = ()  # track player selections
    player_selections = []

    white = False  # true if human is playing as white
    black = False
    move_undone = False
    move_finder_process = None
    ai_thinking = False

    running = True  # Default running state
    game_over = False
    while running:
        human = (game_state.white_to_move and white) or (not game_state.white_to_move and black)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                p.quit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human:
                    loc = p.mouse.get_pos()  # the following logic loads a selection
                    col = loc[0] // square_size
                    row = loc[1] // square_size

                    if selected == (row, col):
                        selected = ()
                        player_selections = []
                    else:
                        selected = (row, col)
                        player_selections.append(selected)

                    if len(player_selections) == 2:
                        move = engine.Move(player_selections[0], player_selections[1], game_state.board)  # make move

                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                to_animate = True
                                selected = ()  # reset user clicks
                                player_selections = []
                        if not move_made:
                            player_selections = [player_selections[1]]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    to_animate = False
                    game_state.undo_move()
                    move_made = True
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:
                    game_state = engine.GameState()
                    valid_moves = game_state.generate_valid_moves()
                    selected = ()
                    player_selections = []
                    move_made = False
                    to_animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        if not game_over and not human and not move_undone:
            if not ai_thinking:
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
                to_animate = True
                ai_thinking = False

        if move_made:
            if to_animate:
                animate(game_state.move_log, display, game_state, clock, to_animate)
                print(game_state.move_log[-1].chess_notation())
            valid_moves = game_state.generate_valid_moves()
            move_made = False
            to_animate = False
            move_undone = False

        draw_game(display, game_state, valid_moves, selected)  # Draw game

        if game_state.is_checkmate():
            game_over = True
            if game_state.white_to_move:
                draw_text(display, "Black wins by checkmate!")
            else:
                draw_text(display, "White wins by checkmate!")
        elif game_state.is_stalemate():
            game_over = True
            draw_text(display, "Stalemate.")

        clock.tick(fps)
        p.display.flip()


"""

THE FOLLOWING ARE HELPER METHODS.

"""


def load_images():  # Loads images of game pieces only once
    pieces = ["bR", "bK", "bB", "bQ", "bN", "bP", "wR", "wK", "wB", "wQ", "wN", "wP"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (square_size, square_size))


def draw_game(display, game_state, valid_moves, selected):  # Draws the current game state
    draw_board(display)
    space_highlighting(display, game_state, valid_moves, selected)
    draw_pieces(display, game_state)


def draw_board(display):  # Draws the board squares
    for row in range(dim):
        for col in range(dim):
            color = board_colors[(row+col) % 2]
            p.draw.rect(display, color, p.Rect(col*square_size, row*square_size, square_size, square_size))


def draw_pieces(display, game_state):  # Draws the pieces
    for row in range(dim):
        for col in range(dim):
            piece = game_state.board[row][col]
            if piece != "  ":
                display.blit(images[piece], p.Rect(col*square_size, row*square_size, square_size, square_size))


def space_highlighting(display, game_state, valid_moves, selection):
    # flag king if in check
    if game_state.inCheck:
        b = p.Surface((square_size, square_size))
        b.set_alpha(100)
        b.fill(p.Color(255, 0, 0))
        if game_state.white_to_move:
            sq = game_state.w_king_loc
            display.blit(b, (square_size * sq[1], square_size * sq[0]))
        else:
            sq = game_state.b_king_loc
            display.blit(b, (square_size * sq[1], square_size * sq[0]))

    # highlight last move
    if len(game_state.move_log) != 0:
        b = p.Surface((square_size, square_size))
        b.set_alpha(100)
        b.fill(p.Color(144, 238, 144))
        sq = game_state.move_log[-1]
        display.blit(b, (square_size * sq.start_col, square_size * sq.start_row))

    if selection != ():
        row, col = selection
        if game_state.board[row][col][0] == ("w" if game_state.white_to_move else "b"):
            h = p.Surface((square_size, square_size))  # highlight the square that is selected
            h.set_alpha(200)
            h.fill(p.Color(211, 211, 211))
            display.blit(h, (col*square_size, row*square_size))
            b = p.Surface((square_size, square_size))  # highlight squares of valid moves for that piece
            b.set_alpha(100)
            b.fill(p.Color(144, 238, 144))
            for move in valid_moves:
                if row == move.start_row and col == move.start_col:
                    display.blit(b, (square_size*move.end_col, square_size*move.end_row))


def animate(move_log, display, board, clock, to_animate):
    if to_animate and len(move_log) != 0:
        move = move_log[-1]
        delta_row = move.end_row - move.start_row
        delta_col = move.end_col - move.start_col
        frames = (abs(delta_row) + abs(delta_col)) * fps  # how many frames will it take to move to each square
        for f in range(frames+1):
            row, col = move.start_row + delta_row*f/frames, move.start_col + delta_col*f/frames
            draw_board(display)
            draw_pieces(display, board)
            board_color = board_colors[(move.end_row + move.end_col) % 2]
            end = p.Rect(move.end_col*square_size, move.end_row*square_size, square_size, square_size)
            p.draw.rect(display, board_color, end)
            if move.piece_captured != "  ":
                display.blit(images[move.piece_captured], end)
            # animate piece moving
            if move.piece_captured != "  ":
                display.blit(images[move.piece_moved], p.Rect(col*square_size, row*square_size, square_size, square_size))
                p.display.flip()
                clock.tick(60)


def draw_text(display, text):
    font = p.font.SysFont("Arial", 33, True, False)
    txt = font.render(text, False, p.Color("white"))
    txt_loc = p.Rect(0, 0, width, height).move(width / 2 - txt.get_width() / 2, height / 2 - txt.get_height() / 2)
    display.blit(txt, txt_loc)

    font = p.font.SysFont("Arial", 32, True, False)
    txt = font.render(text, False, p.Color("black"))
    txt_loc = p.Rect(0, 0, width, height).move(width/2 - txt.get_width()/2, height/2 - txt.get_height()/2)
    display.blit(txt, txt_loc)


if __name__ == "__main__":
    main()

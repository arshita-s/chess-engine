import pygame as p
import engine


# game window details
height = width = 512  # pixels
dim = 8  # Ranks and files
square_size = height // dim
fps = 15
images = {}


def load_images():  # Loads images of game pieces only once
    pieces = ["bR", "bK", "bB", "bQ", "bN", "bP", "wR", "wK", "wB", "wQ", "wN", "wP"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (square_size, square_size))


def draw_game(display, game_state):  # Draws the current game state
    draw_board(display)
    draw_pieces(display, game_state)


def draw_board(display):  # Draws the board squares
    board_colors = [p.Color(255,248,220), p.Color(210,180,140)]
    for row in range(dim):
        for col in range(dim):
            color = board_colors[(row+col)%2]
            p.draw.rect(display, color, p.Rect(col*square_size, row*square_size, square_size, square_size))


def draw_pieces(display, game_state):  # Draws the pieces
    for row in range(dim):
        for col in range(dim):
            piece = game_state.board[row][col]
            if piece != "  ":
                display.blit(images[piece], p.Rect(col*square_size, row*square_size, square_size, square_size))


def main():
    p.init()  # initialize py game

    display = p.display.set_mode((width, height))  # set up game display
    clock = p.time.Clock()
    display.fill(p.Color("white"))

    game_state = engine.GameState()  # initialize game state
    valid_moves = game_state.generate_valid_moves()  # generate valid moves
    move_made = False  # to check whether a move has been made since the last game state update

    load_images()  # load images

    selected = ()  # track player selections
    player_selections = []

    running = True  # Default running state
    while running:

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:

                loc = p.mouse.get_pos()  # the following logic loads a selection
                col = loc[0]//square_size
                row = loc[1]//square_size

                if selected == (row, col):
                    selected = ()
                    player_selections = []
                else:
                    selection = (row, col)
                    player_selections.append(selection)

                if len(player_selections) == 2:
                    move = engine.Move(player_selections[0], player_selections[1], game_state.board)  # make move

                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            game_state.make_move(valid_moves[i])
                            move_made = True
                            selected = ()  # reset user clicks
                            player_selections = []
                    if not move_made:
                        player_selections = [player_selections[1]]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    game_state.undo_move()
                    move_made = True

        if move_made:
            valid_moves = game_state.generate_valid_moves()
            move_made = False

        draw_game(display, game_state)  # Draw game
        clock.tick(fps)
        p.display.flip()


if __name__ == "__main__":
    main()

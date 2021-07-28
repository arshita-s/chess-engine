"""
move_finder.py

??? ai will find moves

"""

import random



piece_scores = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wP": pawn_scores,
                         "bP": pawn_scores[::-1]}

checkmate = 1000
stalemate = 0
D = 3


def find_move_nega_max(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(game_state)
    # move ordering - implement later //TODO
    max_score = -checkmate
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.generate_valid_moves()
        score = -find_move_nega_max(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == D:
                next_move = move
        game_state.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def score_board(game_state):
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    """
    if game_state.is_checkmate():
        if game_state.white_to_move:
            return -checkmate  # black wins
        else:
            return checkmate  # white wins
    elif game_state.is_stalemate():
        return stalemate
    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "  ":
                piece_position_score = 0
                if piece[1] != "K":
                    piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == "w":
                    score += piece_scores[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= piece_scores[piece[1]] + piece_position_score

    return score


def find_random_moves(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]


def find_best_move(game_state, valid_moves, return_queue):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    find_move_nega_max(game_state, valid_moves, D, -checkmate, checkmate, 1 if game_state.white_to_move else -1)
    return_queue.put(next_move)


def find_best_move_old(game_state, valid_moves):
    mux = 1 if game_state.white_to_move else -1
    opp_minmax_score = checkmate
    best_move = None
    random.shuffle(valid_moves)

    for move in valid_moves:
        game_state.make_move(move)
        opponent_moves = game_state.generate_valid_moves()

        if game_state.is_stalemate():
            opp_max_score = stalemate
        elif game_state.is_checkmate:
            opp_max_score = -checkmate
        else:
            opp_max_score = -checkmate
            for m in opponent_moves:
                game_state.make_move(m)
                game_state.generate_valid_moves()
                if game_state.is_checkmate():
                    score = checkmate
                elif game_state.is_stalemate():
                    score = stalemate
                else:
                    score = -mux*score_material(game_state.board)

                if score > opp_max_score:
                    opp_max_score = score
                game_state.undo_move()

        if opp_max_score < opp_minmax_score:
            opp_minmax_score = opp_max_score
            best_move = move
        game_state.undo_move()
    return best_move


def score_material(board):  # find score based on material
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_scores[square[1]]
            elif square[0] == "b":
                score -= piece_scores[square[1]]
    return score
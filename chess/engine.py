"""
engine.py

Defines the GameState, Move, and Castling classes. Responsible for handling the computation of moves, making of moves,
and undoing of moves.

"""


class GameState:  # tracks the current state of the game

    def __init__(self):

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True  # which color's turn
        self.move_log = []  # running log of moves
        self.move_funcs = {"P": self.pawn_moves,
                           "R": self.rook_moves,
                           "N": self.knight_moves,
                           "B": self.bishop_moves,
                           "Q": self.queen_moves,
                           "K": self.king_moves}
        self.w_king_loc = (7, 4)  # white king's location
        self.b_king_loc = (0, 4)  # black king's location
        self.pins = []  # pins in the current game state
        self.checks = []  # checks in the current game state
        self.inCheck = False  # whether a king is in check
        self.can_ep = ()  # coordinates for en passant square
        self.castle_rights = Castling(True, True, True, True)  # current castling rights for both colors
        self.castling_log = [Castling(self.castle_rights.wks, self.castle_rights.wqs,
                                      self.castle_rights.bks, self.castle_rights.bqs)]

        self.checkmate = False
        self.stalemate = False

    def is_checkmate(self):
        if self.inCheck and len(self.generate_valid_moves()) == 0:
            self.checkmate = True
            return True

    def is_stalemate(self):
        if not self.inCheck and len(self.generate_valid_moves()) == 0:
            self.stalemate = True
            return True

    def make_move(self, move):

        self.board[move.start_row][move.start_col] = "  "  # make initial space empty
        self.board[move.end_row][move.end_col] = move.piece_moved  # place piece in end space
        self.move_log.append(move)  # update log
        self.white_to_move = not self.white_to_move  # switch player turn

        # handling pawn promotion
        if move.is_pawn_prom:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # handling en passant moves
        if move.is_ep_move:
            self.board[move.start_row][move.start_col] = "  "
            self.board[move.start_row][move.end_col] = "  "
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.can_ep = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.can_ep = ()

        # handling castling rights
        self.update_castle_rights(move)
        self.castling_log.append(Castling(self.castle_rights.wks, self.castle_rights.wqs,
                                          self.castle_rights.bks, self.castle_rights.bqs))

        # handling castle moves
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = move.piece_moved[0] + "R"
                self.board[move.end_row][move.end_col + 1] = "  "
            else:
                self.board[move.end_row][move.end_col + 1] = move.piece_moved[0] + "R"
                self.board[move.end_row][move.end_col - 2] = "  "

    def undo_move(self):

        if len(self.move_log) != 0:  # only if there is a move to undo, do the reverse of make move
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

            # undo en passant move
            if move.is_ep_move:
                self.board[move.end_row][move.end_col] = "  "
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.can_ep = (move.end_row, move.end_col)

            if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
                self.can_ep = ()

            # undo change in castling rights
            self.castling_log.pop()
            self.castle_rights = self.castling_log[-1]

            # undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col+1] = move.piece_moved[0] + "R"
                    self.board[move.end_row][move.end_col-1] = "  "
                else:
                    self.board[move.end_row][move.end_col + 1] = "  "
                    self.board[move.end_row][move.end_col - 2] = move.piece_moved[0] + "R"
            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move):  # take away castling rights based on moves made

        # if a king or corresponding rook gets moved, certain castling rights are lost
        if move.piece_moved == "wK":
            self.castle_rights.wks = False
            self.castle_rights.wqs = False
        elif move.piece_moved == "bK":
            self.castle_rights.bks = False
            self.castle_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.castle_rights.wqs = False
                elif move.start_col == 7:
                    self.castle_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.castle_rights.bqs = False
                elif move.start_col == 7:
                    self.castle_rights.bks = False

        # if a rook is captured, you can't castle on that side
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.castle_rights.wqs = False
                elif move.end_col == 7:
                    self.castle_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.castle_rights.bqs = False
                elif move.end_col == 7:
                    self.castle_rights.bks = False

    def generate_possible_moves(self):  # generate all possible moves in the current game state
        moves = []

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_funcs[piece](row, col, moves)
        return moves

    def pawn_moves(self, row, col, moves):  # generate all possible pawn moves

        enemy = "b" if self.white_to_move else "w"
        direction = -1 if self.white_to_move else 1
        start_row = 6 if self.white_to_move else 1
        pinned = False
        pin_d = ()

        for i in reversed(range(len(self.pins))):  # check for pins
            if self.pins[i][0] == row and self.pins[i][1] == col:
                pinned = True
                pin_d = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            if self.board[row+(1*direction)][col] == "  ":  # forward movement
                if not pinned or pin_d == (-1, 0):  # this move is only valid if it isn't pinned
                    moves.append(Move((row, col), (row+(1*direction), col), self.board))
                    if row == start_row and self.board[row+(2*direction)][col] == "  ":
                        moves.append(Move((row, col), (row + (2*direction), col), self.board))
            if col - 1 >= 0:  # left capture
                if self.board[row + (1*direction)][col - 1][0] == enemy:
                    if not pinned or pin_d == (-1, -1):
                        moves.append(Move((row, col), (row + (1*direction), col-1), self.board))
                elif (row-1, col-1) == self.can_ep:  # add en passant move
                    moves.append(Move((row, col), (row + (1 * direction), col - 1), self.board, ep=True))
            if col + 1 <= 7:  # right capture
                if self.board[row + (1*direction)][col + 1][0] == enemy:
                    if not pinned or pin_d == (-1, 1):
                        moves.append(Move((row, col), (row + (1*direction), col + 1), self.board))
                elif (row-1, col+1) == self.can_ep:  # add en passant move
                    moves.append(Move((row, col), (row + (1 * direction), col + 1), self.board, ep=True))

        # the same here except for black in the downward direction
        else:
            if self.board[row+(1*direction)][col] == "  ":
                if not pinned or pin_d == (1, 0):
                    moves.append(Move((row, col), (row+(1*direction), col), self.board))
                    if row == start_row and self.board[row+(2*direction)][col] == "  ":
                        moves.append(Move((row, col), (row + (2*direction), col), self.board))
            if col - 1 >= 0:
                if self.board[row + (1*direction)][col - 1][0] == enemy:
                    if not pinned or pin_d == (1, -1):
                        moves.append(Move((row, col), (row + (1*direction), col-1), self.board))
                elif (row+1, col-1) == self.can_ep:
                    moves.append(Move((row, col), (row + (1 * direction), col - 1), self.board, ep=True))
            if col + 1 <= 7:
                if self.board[row + (1*direction)][col + 1][0] == enemy:
                    if not pinned or pin_d == (1, 1):
                        moves.append(Move((row, col), (row + (1*direction), col + 1), self.board))
                elif (row+1, col+1) == self.can_ep:
                    moves.append(Move((row, col), (row + (1 * direction), col + 1), self.board, ep=True))

    def rook_moves(self, row, col, moves):

        enemy = "b" if self.white_to_move else "w"
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up, down, left, right
        pinned = False
        pin_d = ()

        for i in reversed(range(len(self.pins))):  # check for pins
            if self.pins[i][0] == row and self.pins[i][1] == col:
                pinned = True
                pin_d = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":  # don't remove queen pins here
                    self.pins.remove(self.pins[i])
                break

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 7 >= end_row >= 0 and 7 >= end_col >= 0:
                    if not pinned or pin_d == d or pin_d == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "  ":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def bishop_moves(self, row, col, moves):

        enemy = "b" if self.white_to_move else "w"
        directions = ((-1, -1), (-1, 1),  # up left, up right
                      (1, -1), (1, 1))  # down left, down right
        pinned = False
        pin_d = ()

        for i in reversed(range(len(self.pins))):  # check for pins
            if self.pins[i][0] == row and self.pins[i][1] == col:
                pinned = True
                pin_d = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 7 >= end_row >= 0 and 7 >= end_col >= 0:
                    if not pinned or pin_d == d or pin_d == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "  ":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def knight_moves(self, row, col, moves):

        ally = "w" if self.white_to_move else "b"
        directions = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        pinned = False

        for i in reversed(range(len(self.pins))):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                pinned = True
                self.pins.remove(self.pins[i])
                break

        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 7 >= end_row >= 0 and 7 >= end_col >= 0:
                if not pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def queen_moves(self, row, col, moves):
        self.rook_moves(row, col, moves)
        self.bishop_moves(row, col, moves)

    def king_moves(self, row, col, moves):

        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally = "w" if self.white_to_move else "b"

        for i in range(8):

            end_row = row + row_moves[i]
            end_col = col + col_moves[i]

            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:  # not an ally piece - empty or enemy

                    if ally == "w":
                        self.w_king_loc = (end_row, end_col)
                    else:
                        self.b_king_loc = (end_row, end_col)
                    in_check, pins, checks = self.find_pins_checks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    if ally == "w":
                        self.w_king_loc = (row, col)
                    else:
                        self.b_king_loc = (row, col)

    def square_under_attack(self, row, col):

        self.white_to_move = not self.white_to_move  # switch to opponent's point of view
        opponents_moves = self.generate_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def get_castle_moves(self, row, col, moves):
        if self.inCheck:
            return
        if (self.white_to_move and self.castle_rights.wks) or (not self.white_to_move and self.castle_rights.bks):
            self.get_king_side(row, col, moves)
        if (self.white_to_move and self.castle_rights.wqs) or (not self.white_to_move and self.castle_rights.bqs):
            self.get_queen_side(row, col, moves)

    def get_king_side(self, row, col, moves):
        if self.board[row][col+1] == "  " and self.board[row][col+2] == "  ":
            if not self.square_under_attack(row, col+1) and not self.square_under_attack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, castle=True))

    def get_queen_side(self, row, col, moves):
        if self.board[row][col-1] == "  " and self.board[row][col-2] == "  " and self.board[row][col-3]:
            if not self.square_under_attack(row, col-1) and not self.square_under_attack(row, col-2):
                moves.append(Move((row, col), (row, col-2), self.board, castle=True))

    def generate_valid_moves(self):

        temp_ep = self.can_ep
        temp_castling = Castling(self.castle_rights.wks, self.castle_rights.wqs, self.castle_rights.bks,
                                 self.castle_rights.bqs)
        moves = []
        self.inCheck, self.pins, self.checks = self.find_pins_checks()

        if self.white_to_move:  # get the king's current location
            king_row = self.w_king_loc[0]
            king_col = self.w_king_loc[1]
        else:
            king_row = self.b_king_loc[0]
            king_col = self.b_king_loc[1]

        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.generate_possible_moves()
                check = self.checks[0]
                piece_checking = self.board[check[0]][check[1]]
                valid_squares = []

                if piece_checking[1] == "N":  # forced to capture knight or move away
                    valid_squares = [(check[0], check[1])]
                else:  # all other pieces can be blocked
                    for i in range(1, 8):
                        square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(square)
                        if square[0] == check[0] and square[1] == check[1]:
                            break
                for i in reversed(range(len(moves))):  # get rid of moves that don't block the check
                    if moves[i].piece_moved[1] != "K":  # if it's not the king that is being moved...
                        if (moves[i].end_row, moves[i].end_col) not in valid_squares:  # moves that don't block or take
                            moves.remove(moves[i])
            else:  # there is more than one check so the king is forced to move
                self.king_moves(king_row, king_col, moves)

        else:
            moves = self.generate_possible_moves()
            if self.white_to_move:
                self.get_castle_moves(self.w_king_loc[0], self.w_king_loc[1], moves)
            else:
                self.get_castle_moves(self.b_king_loc[0], self.b_king_loc[1], moves)

        self.can_ep = temp_ep
        self.castle_rights = temp_castling
        return moves

    def find_pins_checks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False

        if self.white_to_move:
            enemy = "b"
            ally = "w"
            start_row = self.w_king_loc[0]
            start_col = self.w_king_loc[1]
        else:
            enemy = "w"
            ally = "b"
            start_row = self.b_king_loc[0]
            start_col = self.b_king_loc[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins

            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break

                    elif end_piece[0] == enemy:
                        enemy_type = end_piece[1]

                        # 1. checking piece is ahead of king and is a rook
                        # 2. piece is diagonal from king and is a bishop
                        # 3. a square away diagonally from king and is a pawn
                        # 4. piece is a queen
                        # 5. piece is a king

                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "P" and (
                                (enemy == "w" and 6 <= j <= 7) or (enemy == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board

        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))

        return in_check, pins, checks


class Move:

    def __init__(self, start, end, board, ep=False, castle=False):

        self.start_row = start[0]
        self.start_col = start[1]

        self.end_row = end[0]
        self.end_col = end[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        self.is_pawn_prom = (self.piece_moved == "wP" and self.end_row == 0) or \
                            (self.piece_moved == "bP" and self.end_row == 7)

        self.is_ep_move = ep
        if self.is_ep_move:
            self.piece_captured = "wP" if self.piece_moved[0] == "b" else "bP"

        self.is_castle_move = castle

    # chess notation
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {i: j for j, i in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {i: j for j, i in files_to_cols.items()}

    def chess_notation(self):
        capture = ''

        if self.piece_captured != "  ":
            capture = 'x'

        if self.piece_moved[1] == 'P':
            return self.get_rank_file(self.start_row, self.start_col) + capture \
                   + self.get_rank_file(self.end_row, self.end_col)

        else:
            return self.piece_moved[1] + self.get_rank_file(self.start_row, self.start_col) + capture \
               + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


class Castling:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

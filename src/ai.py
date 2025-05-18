import random, time, copy, numpy as np
import settings


def get_check_pos(col, game_board):
    c = 0
    while not game_board.can_drop(c, col):
        c+=1 #goes up the column until an empty spot is found
        if c>=game_board.height: #if the column is full the move is invalid
            return False
    return (c,col)


def get_valid_moves(game_board):
    check_positions = [get_check_pos(col, game_board) for col in range(settings.BOARD_WIDTH)]
    return [pos[1] for pos in check_positions if pos]


def score_move(col, game_board, player):
    pos = get_check_pos(col, game_board)
    opponent = 1 - player
    score = 0
    if pos:
        for connect in game_board.get_connect_lengths(player + 1, pos):
            if (connect == 2):
                score += 10
            if (connect == 3):
                score += 20
            if (connect > 4):
                score += 1000000
        for connect in game_board.get_connect_lengths(opponent + 1, pos):
            if (connect == 2):
                score += 10
            if (connect == 3):
                score += 50
            if (connect > 4):
                score += 1000
    return score

def score_position(game_board, player):
    scores = [score_move(col, game_board, player) for col in range(settings.BOARD_WIDTH)]
    return sum(scores)


def evaluate(depth, game_board, player):
    if depth == 0:
        return score_position(game_board, player)

    moves = get_valid_moves(game_board)
    if not moves:
        return 0

    best_score = -1e5

    for move in moves:
        new_board = copy.deepcopy(game_board)
        new_board.drop_piece(move)
        score = -evaluate(depth-1, new_board, 1 - player)
        best_score = max(best_score, score)

    return best_score


class AI:
    def __init__(self, board):
        self.gb = board

    def get_move(self):
        moves = []
        for col in get_valid_moves(self.gb):
            new_board = copy.deepcopy(self.gb)
            new_board.drop_piece(col)
            moves.append((col, evaluate(3, new_board, settings.BOT)))
        print(moves)
        highest = max(moves, key=lambda move: move[1])
        if highest[0] == 0:
            return random.randint(0, settings.BOARD_WIDTH - 1)
        return highest[0]

    # below is the original idea for scoring where each column is evaluated at one depth instead of scoring the columns based on
    # the future of the entire board

    # def get_move(self):
    #     time.sleep(1)
    #     scores = [self.score_move(col, settings.BOT) + self.score_move(col, settings.PLAYER)  for col in range(settings.BOARD_WIDTH)]
    #     print(scores)
    #     highest = max(scores)
    #     if highest == 0:
    #         return random.randint(0, settings.BOARD_WIDTH - 1)
    #     return scores.index(highest)
    #
    # def score_position(self, piece):
    #     for row in range(settings.BOARD_HEIGHT):
    #         col = list(self.gb.board[row, :])
    #
    # def score_move(self, col, piece):
    #     # check for wins
    #     pos = self.get_check_pos(col)
    #     if not pos:
    #         return -2000 # for invalid moves
    #     # print(f" checking for win at {pos} with player {piece + 1}")
    #     if piece == settings.BOT:
    #         return 1000 if self.gb.check_win(pos, piece + 1) else 0
    #     if piece == settings.PLAYER:
    #         return 100 if self.gb.check_win(pos, piece + 1) else 0
    #
    # def get_check_pos(self, col):
    #     c = 0
    #     while not self.gb.can_drop(c, col):
    #         c+=1 #goes up the column until an empty spot is found
    #         if c>=self.gb.height: #if the column is full the move is invalid
    #             return False
    #     return (c,col)
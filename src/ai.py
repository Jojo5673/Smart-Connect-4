import random, math, copy, numpy as np, os
import settings
from multiprocessing import Pool
from numpy.lib.stride_tricks import sliding_window_view


def score_windows(windows, piece):
    pc = piece + 1
    opp = (1 - piece) + 1
    piece_count = (windows == pc).sum(axis=1)
    opp_count = (windows == opp).sum(axis=1)
    zero_count = (windows == 0).sum(axis=1)

    score = np.zeros(len(windows))
    score += (piece_count == 4) * (zero_count == 0) * 1500
    score += (piece_count == 3) * (zero_count == 1) * 80
    score += (piece_count == 2) * (zero_count == 2) * 5

    score -= (opp_count == 4) * (zero_count == 0) * 1000
    score -= (opp_count == 3) * (zero_count == 1) * 100
    score -= (opp_count == 2) * (zero_count == 2) * 7
    return int(score.sum())

def score_column(args):
    board, piece, col, depth = args
    ai = AI(board)
    pos = ai.gb.drop_piece(col, piece)
    score = ai.evaluate(piece, depth, -math.inf, math.inf)
    ai.gb.undo(pos)
    return col, score

class AI:
    def __init__(self, board):
        self.gb = board
        self.depth = 6

    def get_check_pos(self, col):
        c = 0
        while not self.gb.can_drop(c, col):
            c += 1  # goes up the column until an empty spot is found
            if c >= self.gb.height:  # if the column is full the move is invalid
                return False
        return (c, col)

    def get_ordered_moves(self, piece):
        moves = self.gb.get_valid_moves()
        center = settings.CENTER_COL
        moves.sort(key=lambda col: abs(center-col)) #tries out center first to optimize alpha beta
        return moves

    def get_move(self, piece):
        valid_moves = self.get_ordered_moves(piece)

        args = [(copy.deepcopy(self.gb), piece, col, self.depth) for col in valid_moves]

        with Pool(processes=min(len(valid_moves), os.cpu_count())) as pool:
            results = pool.map(score_column, args)

        best_col, best_score = max(results, key=lambda x: (x[1], random.randint(0,7)))
        return best_col


    def evaluate(self, piece, depth, alpha, beta):
        player_score = self.score_position(piece)
        if depth == 0 or self.gb.return_game_over():
            return player_score

            # for opponent
        opp_piece = 1 - piece
        best_opp_score = -math.inf
        valid_moves = self.get_ordered_moves(piece)
        # best_opp_col = 0
        for col in valid_moves:
            pos = self.gb.drop_piece(col, opp_piece)
            score = self.evaluate(opp_piece, depth - 1, -beta, -alpha)
            if score > best_opp_score:
                best_opp_score = score  # redundant ik but im keeping it for debug
                # best_opp_col = col
            self.gb.undo(pos)
            alpha = max(alpha, best_opp_score)
            if beta <= alpha:
                break
        return player_score - best_opp_score


    def score_position(self, piece):
        score = 0
        # score center column
        center_col = self.gb.board[:, settings.CENTER_COL]
        center_count = (center_col == piece + 1) * 3
        score += int(center_count.sum())
        # checks slices of 4 across the whole self.gb.board

        horizontal_windows = sliding_window_view(self.gb.board, (1, 4)).reshape(-1, 4)
        vertical_windows = sliding_window_view(self.gb.board, (4, 1)).reshape(-1, 4)
        pos_diag = sliding_window_view(self.gb.board, (4, 4))
        pos_diag = np.array(
            [pos_diag[i, j].diagonal() for i in range(pos_diag.shape[0]) for j in range(pos_diag.shape[1])])

        flipped = np.fliplr(self.gb.board)
        neg_diag = sliding_window_view(flipped, (4, 4))
        neg_diag = np.array(
            [neg_diag[i, j].diagonal() for i in range(neg_diag.shape[0]) for j in range(neg_diag.shape[1])])

        windows = np.concatenate([horizontal_windows, vertical_windows, pos_diag, neg_diag])

        score += score_windows(windows, piece)
        return score



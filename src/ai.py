import random, time, math, numpy as np
import settings

def score_window(window, piece):
    opp = 1 - piece
    score = 0
    if window.count(piece + 1) == 4:
        score += 1500
    elif window.count(piece + 1) == 3 and window.count(0) == 1:
        score += 80
    elif window.count(piece + 1) == 2 and window.count(0) == 2:
        score += 5

    if window.count(opp + 1) == 4:
        score -= 1000
    elif window.count(opp + 1) == 3 and window.count(0) == 1:
        score -= 100
    elif window.count(opp + 1) == 2 and window.count(0) == 2:
        score -= 7
    return score

class AI:
    def __init__(self, board):
        self.gb = board
        self.depth = 4

    def get_check_pos(self, col):
        c = 0
        while not self.gb.can_drop(c, col):
            c += 1  # goes up the column until an empty spot is found
            if c >= self.gb.height:  # if the column is full the move is invalid
                return False
        return (c, col)

    # def get_move(self, piece):
    #     moves = []
    #     valid_moves = self.gb.get_valid_moves()
    #     best_col = random.choice(valid_moves)
    #     best_score = -math.inf
    #     for col in valid_moves:
    #         pos = self.gb.drop_piece(col, piece)
    #         # score = self.score_position(piece) - self.opp_best_score_after_play(1-piece)
    #         score = self.evaluate(piece, self.depth)
    #         print((col, score))
    #         if score > best_score:
    #             best_score = score
    #             best_col = col
    #         self.gb.undo(pos)
    #     return best_col
    #
    # def evaluate(self, piece, depth):
    #     player_score = self.score_position(piece)
    #     if depth == 0 or self.gb.return_game_over():
    #         return player_score
    #
    #         #for opponent
    #     opp_piece =  1 - piece
    #     best_opp_score = -math.inf
    #     valid_moves = self.gb.get_valid_moves()
    #     # best_opp_col = 0
    #     for col in valid_moves:
    #         pos = self.gb.drop_piece(col, opp_piece)
    #         score = self.evaluate(opp_piece, depth - 1)
    #         if score > best_opp_score:
    #             best_opp_score = score
    #             # best_opp_col = col
    #         self.gb.undo(pos)
    #     return player_score - best_opp_score

    def get_move(self, piece):
        moves = []
        valid_moves = self.gb.get_valid_moves()
        best_col = random.choice(valid_moves)
        best_score = -math.inf
        for col in valid_moves:
            pos = self.gb.drop_piece(col, piece)
            # score = self.score_position(piece) - self.opp_best_score_after_play(1-piece)
            score = self.evaluate(piece, self.depth, -math.inf, math.inf)
            print((col, score))
            if score > best_score:
                best_score = score
                best_col = col
            self.gb.undo(pos)
        return best_col

    def evaluate(self, piece, depth, alpha, beta):
        player_score = self.score_position(piece)
        if depth == 0 or self.gb.return_game_over():
            return player_score

            # for opponent
        opp_piece = 1 - piece
        best_opp_score = -math.inf
        valid_moves = self.gb.get_valid_moves()
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
        #score center column
        center_col = list(self.gb.board[:,settings.BOARD_WIDTH//2])
        score += center_col.count(piece + 1) * 3
        #checks slices of 4 across the whole board
        #horizontal
        for row in self.gb.board:
            for col in range(settings.BOARD_WIDTH - 3):
                window = list(row[col:col+4])
                score += score_window(window, piece)

        #vertical
        for c in range(settings.BOARD_WIDTH):
            col = self.gb.board[:,c]
            for row in range(settings.BOARD_HEIGHT - 3):
                window = list(col[row:row+4])
                score += score_window(window, piece)

        #diagonal
        for c in range(settings.BOARD_WIDTH - 3):
            for r in range(settings.BOARD_HEIGHT - 3):
                window = []
                for i in range(4):
                    window.append(self.gb.board[r+i][c+i])
                score += score_window(window, piece)

        #anti-diagonal
        for c in range(settings.BOARD_WIDTH - 4, settings.BOARD_WIDTH):
            for r in range(settings.BOARD_HEIGHT - 3):
                window = []
                for i in range(4):
                    window.append(self.gb.board[r+i][c-i])
                score += score_window(window, piece)
        return score

    # def get_move(self, piece):
    #     moves = []
    #     valid_moves = self.gb.get_valid_moves()
    #     best_col = random.choice(valid_moves)
    #     best_score = -math.inf
    #     for col in valid_moves:
    #         pos = self.gb.drop_piece(col, piece)
    #         # score = self.score_position(piece) - self.opp_best_score_after_play(1-piece)
    #         score = self.evaluate(piece, self.depth, -math.inf, math.inf)
    #         print((col, score))
    #         if score > best_score:
    #             best_score = score
    #             best_col = col
    #         self.gb.undo(pos)
    #     return best_col
    #
    # def evaluate(self, piece, depth, alpha, beta):
    #     player_score = self.score_position(piece)
    #     if depth == 0 or self.gb.return_game_over():
    #         return player_score
    #
    #         # for opponent
    #     opp_piece = 1 - piece
    #     best_opp_score = -math.inf
    #     valid_moves = self.gb.get_valid_moves()
    #     # best_opp_col = 0
    #     for col in valid_moves:
    #         pos = self.gb.drop_piece(col, opp_piece)
    #         score = self.evaluate(opp_piece, depth - 1, -beta, -alpha)
    #         if score > best_opp_score:
    #             best_opp_score = score  # redundant ik but im keeping it for debug
    #             # best_opp_col = col
    #         self.gb.undo(pos)
    #         alpha = max(alpha, best_opp_score)
    #         if beta <= alpha:
    #             break
    #
    #     return player_score - best_opp_score

    # def opp_best_score_after_play(self, piece):
    #     best_score = -10e6
    #     valid_moves = self.gb.get_valid_moves()
    #     best_col = 0
    #     for col in valid_moves:
    #         pos = self.gb.drop_piece(col, piece)
    #         score = self.score_position(piece)
    #         if score > best_score:
    #             best_score = score
    #             best_col = col
    #         self.gb.undo(pos)
    #     #print(f"Opponent best move is {(best_col, best_score)}")
    #     return best_score
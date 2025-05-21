import random, time, numpy as np
import settings

def score_window(window, piece):
    opp = 1 - piece
    score = 0
    if window.count(piece + 1) == 4:
        score += 500
    elif window.count(piece + 1) == 3 and window.count(0) == 1:
        score += 80
    elif window.count(piece + 1) == 2 and window.count(0) == 2:
        score += 5

    if window.count(opp + 1) == 4:
        score -= 700
    elif window.count(opp + 1) == 3 and window.count(0) == 1:
        score -= 100
    elif window.count(opp + 1) == 2 and window.count(0) == 2:
        score -= 7
    return score

class AI:
    def __init__(self, board):
        self.gb = board

    def get_move(self, piece):
        time.sleep(1)
        moves = []
        valid_moves = self.gb.get_valid_moves()
        best_col = random.choice(valid_moves)
        best_score = -10e6
        for col in valid_moves:
            pos = self.gb.drop_piece(col, piece)
            score = self.score_position(piece) - self.opp_best_score_after_play(1-piece)
            print((col, score))
            if score > best_score:
                best_score = score
                best_col = col
            self.gb.undo(pos)
        return best_col

    def get_check_pos(self, col):
        c = 0
        while not self.gb.can_drop(c, col):
            c += 1  # goes up the column until an empty spot is found
            if c >= self.gb.height:  # if the column is full the move is invalid
                return False
        return (c, col)

    def opp_best_score_after_play(self, piece):
        best_score = -10e6
        valid_moves = self.gb.get_valid_moves()
        best_col = 0
        for col in valid_moves:
            pos = self.gb.drop_piece(col, piece)
            score = self.score_position(piece)
            if score > best_score:
                best_score = score
                best_col = col
            self.gb.undo(pos)
        #print(f"Opponent best move is {(best_col, best_score)}")
        return best_score

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

    # TODO: MAKE MINIMAX WORK AT SOME POINT 🙏😭

    # def game_over(self, pos):
    #     return self.gb.check_win(settings.BOT + 1, pos) or self.gb.check_win(settings.PLAYER + 1, pos) or len(
    #         self.gb.get_valid_moves()) == 0

    # def evaluate(self, depth, alpha, beta, pos, is_maximizing):
    #     moves = self.gb.get_valid_moves()
    #     is_game_over = self.game_over(pos)
    #     if depth == 0 or self.game_over(pos):
    #         if is_game_over:
    #             if self.gb.check_win(settings.BOT + 1, pos):
    #                 return 1e7
    #             elif self.gb.check_win(settings.PLAYER + 1, pos):
    #                 return 1e7
    #             else:
    #                 return 0
    #         else:
    #             return self.score_position(settings.BOT)
    #
    #     if is_maximizing:
    #         score = -math.inf
    #         for move in moves:
    #             new_pos = self.gb.drop_piece(move, settings.BOT)
    #             score = max(score, self.evaluate(depth - 1, alpha, beta, new_pos, False))
    #             self.gb.undo(new_pos)
    #             alpha = max(alpha, score)
    #             if alpha >= beta:
    #                 break
    #         return score
    #     else:
    #         score = math.inf
    #         for move in moves:
    #             new_pos = self.gb.drop_piece(move, settings.PLAYER)
    #             score = min(score, self.evaluate(depth - 1, alpha, beta, new_pos, True))
    #             self.gb.undo(new_pos)
    #             beta = min(beta, score)
    #             if alpha >= beta:
    #                 break
    #         return score

import random, time, numpy as np
import settings


class AI:
    def __init__(self, board):
        self.gb = board

    def get_move(self):
        time.sleep(1)
        moves = [(col, self.evaluate(col)) for col in self.get_valid_moves()]
        print(moves)
        highest = max(moves, key=lambda move: move[1])
        if highest == 0:
            return random.randint(0, settings.BOARD_WIDTH - 1)
        return highest[0]

    def evaluate(self, col):
        # TODO: need to somehow get it to make a move and evaluate the board after it does that

        #for now: we just use the simple old thing
        return self.score_move(col, settings.BOT) + self.score_move(col, settings.PLAYER)
        pass

    def score_position(self):
        # for row in range(settings.BOARD_HEIGHT):
        #     col = list(self.gb.board[row, :])

        # TODO: score column is a move evaluator. figure out how to turn use that in this board evaluator here
        scores = [self.score_move(col, settings.BOT) + self.score_move(col, settings.PLAYER) for col in
                  range(settings.BOARD_WIDTH)]
        return sum(scores)

    def score_move(self, col, piece):
        pos = self.get_check_pos(col)
        score = 0
        # print(f" checking for win at {pos} with player {piece + 1}")
        if piece == settings.BOT:
            for connect in self.gb.get_connect_lengths(settings.BOT + 1, pos):
                if (connect == 2):
                    score += 2
                if (connect == 3):
                    score += 5
                if (connect == 4):
                    score += 100
        if piece == settings.PLAYER:
            for connect in self.gb.get_connect_lengths(settings.PLAYER + 1, pos):
                if (connect == 2):
                    score += 2
                if (connect == 3):
                    score += 10
                if (connect == 4):
                    score += 50
        return score

    def get_check_pos(self, col):
        c = 0
        while not self.gb.can_drop(c, col):
            c+=1 #goes up the column until an empty spot is found
            if c>=self.gb.height: #if the column is full the move is invalid
                return False
        return (c,col)

    def get_valid_moves(self):
        check_positions = [self.get_check_pos(col) for col in range(settings.BOARD_WIDTH)]
        return [pos[1] for pos in check_positions]

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
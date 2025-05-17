import random, time, numpy as np
import settings


class AI:
    def __init__(self, board):
        self.board = board

    def get_move(self):
        time.sleep(1)
        return random.choice(range(len(self.board)))
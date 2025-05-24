import random, math, copy, numpy as np, os
import settings
from multiprocessing import Pool
from numpy.lib.stride_tricks import sliding_window_view


def score_windows(windows, piece):

    #performs mass counting and scoring on all the possible 1x4 windows

    #the + 1 is because of my turn system not lining with the pieces on the board
    #i am sorry. i will not be changing it.
    pc = piece + 1
    opp = (1 - piece) + 1

    #imainge the windows array as a 2d array (array of window arrays)
    #(windows == x).sum(axis=1) counts every instance of x along the horizontal axis (the axis of our window's values)
    # this count is put into an array representing the row that was searched
    piece_count = (windows == pc).sum(axis=1)
    opp_count = (windows == opp).sum(axis=1)
    zero_count = (windows == 0).sum(axis=1)
    #for every window, we count your piece, the opponent, and the zeroes (empty holes)
    #remember groups of 2 and 3 are only valuable if they can be connected
    #i.e. there are empty holes that have the potential to make thema 4 in a row

    score = np.zeros(len(windows))
    #starts of score with an empty array and uses numpy array addition to score the counted piece arrays
    score += (piece_count == 4) * (zero_count == 0) * 1500
    score += (piece_count == 3) * (zero_count == 1) * 80
    score += (piece_count == 2) * (zero_count == 2) * 5

    score -= (opp_count == 4) * (zero_count == 0) * 1000
    score -= (opp_count == 3) * (zero_count == 1) * 100
    score -= (opp_count == 2) * (zero_count == 2) * 7

    # * between array comparisons is equivalent to boolean 'and' and returns an array of true or false depending on condition
    # multiplying that results by a numerical weight will replace trues with that weight and False with 0
    # essentially we vector matrix multiplication by a scalar
    #we return the sum of our score vector
    return int(score.sum())

def score_column(args):
    # this is what gets called by the pool.map() executor to run in parallel
    # arguments are passed in an args tuple
    # each process created by pool.map() gets a different column to send here
    # they dont have shared memory so we have to make a new AI instance
    board, piece, col, depth = args
    ai = AI(board)
    pos = ai.gb.drop_piece(col, piece)
    score = ai.evaluate(piece, depth, -math.inf, math.inf)
    ai.gb.undo(pos)
    return col, score

class AI:
    def __init__(self, board):
        self.gb = board
        self.depth = 3

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
        moves.sort(key=lambda col: abs(center-col))
        #orders the legal moves to play center first
        #center moves usually pay out more so this aims to optimize alpha beta pruning
        return moves

    def get_move(self, piece):
        valid_moves = self.get_ordered_moves(piece)

        #the Pool.map() function allows the processing of a function in parallel across multiple inputs
        #this is an optimization technique used to evaluate the player's legal moves in parallel
        args = [(copy.deepcopy(self.gb), piece, col, self.depth) for col in valid_moves]
        with Pool(processes=min(len(valid_moves), os.cpu_count())) as pool:
            results = pool.map(score_column, args)

        #this gets the column that resulted in the best evaluation
        #a random selection is added as a secondary sort key to make the bot randomly select between two best moves
        best_col, best_score = max(results, key=lambda x: (x[1], random.randint(0,7)))
        return best_col


    def evaluate(self, piece, depth, alpha, beta):
        #alpha/beta optimization to avoid looking at move branches the opponent would never allow
        #alpha is our best guaranteed move and we want to maximise it
        #beta is our opponent's best guaranteed move and we want to minimise it
        player_score = self.score_position(piece) #the heuristic score the current position
        if depth == 0 or self.gb.return_game_over():
            return player_score #returns the heuristic score at the end of the tree

        #the evaluation is a variation on the negamax variation of the minimax algorithm
        #the game score isnt zero-sum as would it be in a typical negamax
        #your score is influenced by the best your opponent can do in response
        opp_piece = 1 - piece
        best_opp_score = -math.inf #-infinity so no number can be smaller than it to start
        valid_moves = self.get_ordered_moves(piece)
        for col in valid_moves:
            #recursively scores all the legal moves in the given position and gets the best possible score for the opponent
            pos = self.gb.drop_piece(col, opp_piece)
            score = self.evaluate(opp_piece, depth - 1, -beta, -alpha)
            if score > best_opp_score:
                best_opp_score = score  # redundant ik but im keeping it for debug
            self.gb.undo(pos)
            alpha = max(alpha, best_opp_score) #this is from the perspective of our opponent
            #they are trying to maximise their best guaranteed move here
            #from the opponents view we are the beta they want to minimise
            # however, if they end up with a move too good they know we wont allow it so dont even bother looking there
            if beta <= alpha:
                break
        return player_score - best_opp_score


    def score_position(self, piece):
        score = 0
        # score center column
        center_col = self.gb.board[:, settings.CENTER_COL]
        center_count = (center_col == piece + 1) * 3
        score += int(center_count.sum())

        # checks every possible 1 dimensional slice of 4 pieces across the whole board (1x4 window)
        # it then scores each window depending on if it has 2, 3 or 4 pieces with empty squares remaining
        # so the score is basically a measure of the boards potential

        #returns every 1 row high, 4 column wide slice as a long list of windows
        horizontal_windows = sliding_window_view(self.gb.board, (1, 4)).reshape(-1, 4)

        # returns every 4 row high, 1 column wide slice as a long list of windows
        vertical_windows = sliding_window_view(self.gb.board, (4, 1)).reshape(-1, 4)

        #takes all the 4x4 windows and for every window gets its diagonal as a long list of windows
        pos_diag = sliding_window_view(self.gb.board, (4, 4))
        pos_diag = np.array(
            [pos_diag[i, j].diagonal() for i in range(pos_diag.shape[0]) for j in range(pos_diag.shape[1])])

        #flips the board to get the anti-diagonals
        flipped = np.fliplr(self.gb.board)
        neg_diag = sliding_window_view(flipped, (4, 4))
        neg_diag = np.array(
            [neg_diag[i, j].diagonal() for i in range(neg_diag.shape[0]) for j in range(neg_diag.shape[1])])

        #combines all the window lists into one array or windows that we can do mass operations on to count things
        windows = np.concatenate([horizontal_windows, vertical_windows, pos_diag, neg_diag])

        score += score_windows(windows, piece)
        return score



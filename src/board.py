import random, numpy as np
import settings

#turn alternates between 0 and 1
#pieces on the board are turn + 1
# (yes this is a confusing system that could have easily been made consistent)
# (yes there are dozens of methods to make this consistent and i didnt think of any when i started this part months ago)
# (yes im too lazy to change it)

class Board:
    def __init__(self):
        self.height, self.width = settings.BOARD_HEIGHT, settings.BOARD_WIDTH
        self.screen_dims = settings.SCREEN_DIMS
        self.board =  np.zeros((self.height, self.width))
        self.game_over = False
        self.turn = random.choice((0, 1))
        self.msg = "Your turn" if self.turn == 0 else "Bot's turn"

    def can_drop(self, row, column):
        return self.board[row][column] == 0 #tests if the board is empty at a position

    def check_win(self, player, pos):
        # works by getting the location of the most recent move and its player and checking its immediate surroundings for the player's peices
        # every location is taken and explored in its relative direction from the most recent move for 4 consecutive pieces in that direction
        def check_at(check_pos):  # helper function to check for the player that made the move at specific locations
            if check_pos[0] != self.height and check_pos[1] != self.width and check_pos[0] != -1 and check_pos[1] != -1:
                if self.board[check_pos[0]][check_pos[1]] and self.board[check_pos[0]][check_pos[1]] == player:
                    # checks if the test position exists on the baord and if there is a player there
                    return True
            else:
                return False

        # makes a list of the direction of all the adjacent pieces to the most recent drop
        step_vectors = []
        longest = 0
        # checks the adjacent board positions except (0,0) which is the position being tested
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if check_at((pos[0] + i, pos[1] + j)) and (i, j) != (0, 0):
                    # if a piece is found at an adjacent position it is added to step vectors
                    step_vectors.append((i, j))
        for step in step_vectors:  # goes through the directions of all adjacent pieces and explores them in a loop
            forward = 0
            backward = 0

            search = True
            step_pos = pos
            depth = 0
            #we are going to search forward and backward along a step vector to see if the piece we drop connects any 4 in a rows
            while search: #searches forward along a step vector
                # a new board position is created for testing by adding the direction vector to the start position
                step_pos = (step_pos[0] + step[0], step_pos[1] + step[1])
                if check_at(step_pos):  # if the player is found at the new position the length of the connect is incremented
                    depth += 1
                else:
                    search = False  # stops searching at the end of the connect
                    forward = depth  # stores the longest connect found

            step_pos = pos
            depth = 0
            search = True
            while search: #searches backward along a step vector
                step_pos = (step_pos[0] - step[0], step_pos[1] - step[1])
                if check_at(step_pos):
                    depth += 1
                else:
                    search = False
                    backward = depth
            longest = max(forward + backward + 1, longest)
        return longest >= 4

    #initialises board and game variables
    def drop_piece(self, col, piece):
        c = 0
        while not self.can_drop(c, col):
            c+=1 #goes up the column until an empty spot is found
            if c>=self.height: #if the column is full the move is invalid
                return False
        self.board[c][col] = piece+1 #places the value of the player at the drop position  # alternates the turn between 0 and 1
        return (c,col)
        #returns the location of the dropped piece if its a valid move else false

    def undo (self, pos): #used for resetting the boards after the ai explores them
        self.board[pos[0]][pos[1]] = 0

    def get_valid_moves(self):
        moves = []
        for col in range(self.width):
            piece = self.drop_piece(col, self.turn) #if you can drop the piece it's a valid move fr
            if piece:
                moves.append(col)
                self.undo(piece)
        return moves

    def advance_turn(self, selection):
        #players are stored as 0 and 1, but outputted as 1 and 2
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            self.game_over = True
            self.msg = "Draw" #ends the game when you draw
        drop = self.drop_piece(selection, self.turn) #stores the position of the dropped piece
        if not drop:
            print("invalid move") #if drop returns false the move is invalud
        else:
            if self.check_win(self.turn + 1, drop): #checks every dropped piece for a winning move
                self.msg = f"You win" if self.turn == 0 else f"You lose"
                print(f"You win at {drop}" if self.turn == 0 else f"You lose at {drop}")
                self.game_over = True #ends the game when you win or lose
            else:
                self.msg = "Your turn" if self.turn == 1 else "Bot's turn"
            self.turn = (self.turn + 1) % 2 #cycles the turn between 0 and 1
        return drop

    def return_game_over(self):
        return self.game_over


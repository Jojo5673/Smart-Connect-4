from operator import truediv
import pygame
import numpy as np
import game_func as gf

def create_board(size):
    return np.zeros(size) #gets a matrix from numpy

def draw_board(game_board):
    print(np.flip(game_board, 0)) #makes the game play from bottom up like real connect 4
    print(' ', *map(lambda i: str(i)+' ',list(range(len(game_board[0])))))  #draws the matrix of zeros with correct spacing

def drop_piece(pos):
    c = 0
    while not can_drop(c, pos):
        c+=1 #goes up the column until an empty spot is found
        if c>=height: #if the column is full the move is invalid
            return False
    board[c][pos] = turn+1 #places the value of the player at the drop position
    return (c,pos)
    #returns the location of the dropped piece if its a valid move else false

def can_drop(row, column):
    #print(row - 1, column)
    return board[row][column] == 0 #tests if the board is empty at a position

def check_win(pos, player):
    #this function checks if every new move is a winning move
    #works by getting the location of the most recent move and its player and checking its immediate surroundings for the player's peices
    #every location is taken and explored in its relative direction from the most recent move for 4 consecutive pieces in that direction
    def check_at(check_pos, player): #helper function to check for the player that made the move at specific locations
        if board[check_pos[0]][check_pos[1]] and board[check_pos[0]][check_pos[1]] == player:
            #checks if the test position exists on the baord and if there is a player there
            return True
        else:
            return False

    #makes a list of the direction of all the adjacent pieces to the most recent drop
    step_vectors = []
    longest = 1 #keeps track of the longest line of connects
    #checks the adjacent board positions except (0,0) which is the position being tested
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            if check_at((pos[0] + i,pos[1] + j), player) and (i,j) != (0,0):
                #if a piece is found at an adjacent position it is added to step vectors
                step_vectors.append((i,j))

    for step in step_vectors: #goes through the directions of all adjacent pieces and explores them in a loop
        search = True
        new_pos = pos
        depth = 0
        while search:
            #a new board position is created for testing by adding the direction vector to the start position
            new_pos = (new_pos[0]+step[0], new_pos[1]+step[1])
            #print(new_pos)
            if check_at(new_pos, player): #if the player is found at the new position the length of the connect is incremented
                depth+=1
            else:
                search = False #stops searching at the end of the connect
                longest = max(longest, depth+1) #stores the longest connect found
            #print(longest, depth, step)
    if longest >= 4: #when a connect of 4 pieces is found then the player has won
        return True
    else:
        return False

pygame.init()
height, width = 6,7
screen_dims = (1280,720)
board = create_board((height, width))
game_over = False
turn = 0
pygame.display.set_caption('Connect 4')
screen = pygame.display.set_mode(screen_dims)

#initialises board and game variables

while not game_over:
    gf.check_events()
    draw_board(board)
    #players are stored as 0 and 1, but outputted as 1 and 2
    selection = int(input(f"Player {turn+1}'s move: "))
    drop = drop_piece(selection) #stores the position of the dropped piece
    if not drop:
        print("invalid move") #if drop returns false the move is invalud
    else:
        if check_win(drop, turn + 1): #checks every dropped piece for a winning move
            draw_board(board)
            print(f"Player {turn + 1} wins!")
            game_over = True
        turn = (turn+1)%2 #alternates the turn between 0 and 1

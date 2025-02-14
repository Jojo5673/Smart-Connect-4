import numpy as np

def create_board(size):
    return np.zeros(size)

def draw_board(game_board):
    print(np.flip(game_board, 0))
    print(' ', *map(lambda i: str(i)+' ',list(range(len(game_board[0])))))

def drop_piece(pos):
    c = 0
    while not can_drop(c, pos):
        c+=1
        if c>=height:
            return False
    board[c][pos] = turn+1
    return True

def can_drop(row, column):
    #print(row - 1, column)
    return board[row][column] == 0

height, width = 6,7
board = create_board((height, width))
game_over = False
turn = 0

while not game_over:
    draw_board(board)
    selection = int(input(f"Player {turn+1}'s move: "))
    if not drop_piece(selection):
        print("invalid move")
    turn = (turn+1)%2

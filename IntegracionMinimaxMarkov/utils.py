# utils.py

PLAYER = 'X'
AI = 'O'

def check_winner(board, player):
    for i in range(3):
        if all(cell == player for cell in board[i]): return True
        if all(board[j][i] == player for j in range(3)): return True
    if all(board[i][i] == player for i in range(3)): return True
    if all(board[i][2 - i] == player for i in range(3)): return True
    return False

def is_full(board):
    return all(cell != ' ' for row in board for cell in row)

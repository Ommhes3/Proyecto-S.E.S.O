import tkinter as tk
from tkinter import messagebox
import copy
from tttMarkov.markovModel import MarkovAI




PLAYER = 'X'
AI = 'O'

def check_winner(board, player):
    # filas, columnas y diagonales
    for i in range(3):
        if all([cell == player for cell in board[i]]): return True
        if all([board[j][i] == player for j in range(3)]): return True
    if all([board[i][i] == player for i in range(3)]): return True
    if all([board[i][2 - i] == player for i in range(3)]): return True
    return False

def is_full(board):
    return all(cell != ' ' for row in board for cell in row)

def minimax(board, is_maximizing):
    if check_winner(board, AI):
        return 1
    if check_winner(board, PLAYER):
        return -1
    if is_full(board):
        return 0

    if is_maximizing:
        best = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = AI
                    score = minimax(board, False)
                    board[i][j] = ' '
                    best = max(score, best)
        return best
    else:
        best = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = PLAYER
                    score = minimax(board, True)
                    board[i][j] = ' '
                    best = min(score, best)
        return best

def best_move(board):
    best_score = -float('inf')
    move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = AI
                score = minimax(board, False)
                board[i][j] = ' '
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move

class TicTacToe:
    def __init__(self, root):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.root = root
        self.create_widgets()

    def create_widgets(self):
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.root, text=' ', font=('Arial', 40), width=5, height=2,
                                command=lambda i=i, j=j: self.player_move(i, j))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

    def player_move(self, i, j):
        if self.board[i][j] == ' ':
            self.board[i][j] = PLAYER
            self.buttons[i][j].config(text=PLAYER, state='disabled')
            if check_winner(self.board, PLAYER):
                messagebox.showinfo("Ganaste!", "¡Eres una pro! 😸")
                self.reset()
                return
            elif is_full(self.board):
                messagebox.showinfo("Empate", "¡Nadie ganó! 💤")
                self.reset()
                return
            self.ai_turn()

    def ai_turn(self):
        board_state = tuple(cell if cell != ' ' else '_' for row in self.board for cell in row)
        available = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == ' ']

        move = self.ai.predict_next_move(board_state, available)
        if move in available:
            print("Respuesta encontrada por Markov 🧠")
        else:
            move = best_move(copy.deepcopy(self.board))
            print("Respuesta encontrada por Minimax 🤖")
        
        if move:
            i, j = move
            self.board[i][j] = AI
            self.buttons[i][j].config(text=AI, state='disabled')
            self.ai.record_player_move(board_state, move)

            if check_winner(self.board, AI):
                messagebox.showinfo("Perdiste", "La IA usó su SESO 😈")
                self.ai.end_game()
                self.reset()
            elif is_full(self.board):
                messagebox.showinfo("Empate", "¡Nadie ganó! 💤")
                self.ai.end_game()
                self.reset()
    def reset(self):
        self.ai.end_game()  # guarda el aprendizaje
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=' ', state='normal')


# Lanzar la app
root = tk.Tk()
root.title("Tic Tac Toe con IA 💖")
app = TicTacToe(root)
root.mainloop()

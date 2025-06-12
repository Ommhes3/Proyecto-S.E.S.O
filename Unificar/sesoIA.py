import json
import random
import copy
import os
import tkinter as tk
from tkinter import messagebox

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

class MarkovAI:
    def __init__(self, data_file='markov_learning.json'):
        self.data_file = data_file
        self.transition_counts = {}
        self.history = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 0:
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.transition_counts = {
                        tuple(eval(state)): {tuple(map(int, k.split(','))): v for k, v in moves.items()}
                        for state, moves in data.items()
                    }
            except (json.JSONDecodeError, SyntaxError):
                print("Archivo JSON corrupto o mal formado, iniciando con datos vacíos.")
                self.transition_counts = {}
        else:
            self.transition_counts = {}

    def save_data(self):
        data = {
            str(state): {f"{k[0]},{k[1]}": v for k, v in moves.items()}
            for state, moves in self.transition_counts.items()
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def update_model(self, prev_state, move):
        if prev_state not in self.transition_counts:
            self.transition_counts[prev_state] = {}
        if move not in self.transition_counts[prev_state]:
            self.transition_counts[prev_state][move] = 0
        self.transition_counts[prev_state][move] += 1

    def predict_next_move(self, state, available_moves, board=None):
        move = None
        source = ""

        if state in self.transition_counts and self.transition_counts[state]:
            move_counts = self.transition_counts[state]
            filtered_moves = {move: count for move, count in move_counts.items() if move in available_moves}

            if filtered_moves:
                total = sum(filtered_moves.values())
                moves = list(filtered_moves.keys())
                probabilities = [count / total for count in filtered_moves.values()]
                move = random.choices(moves, weights=probabilities, k=1)[0]
                source = "Markov "

        if move is None and board:
            move = self.get_minimax_move(board)
            if move:
                source = "Minimax "

        if move:
            print(f"Respuesta encontrada por {source}")
            self.record_player_move(state, move)

        return move

    def get_minimax_move(self, board):
        def minimax(b, is_maximizing):
            if check_winner(b, AI): return 1
            if check_winner(b, PLAYER): return -1
            if is_full(b): return 0

            if is_maximizing:
                best = -float('inf')
                for i in range(3):
                    for j in range(3):
                        if b[i][j] == ' ':
                            b[i][j] = AI
                            score = minimax(b, False)
                            b[i][j] = ' '
                            best = max(score, best)
                return best
            else:
                best = float('inf')
                for i in range(3):
                    for j in range(3):
                        if b[i][j] == ' ':
                            b[i][j] = PLAYER
                            score = minimax(b, True)
                            b[i][j] = ' '
                            best = min(score, best)
                return best

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

    def record_player_move(self, state, move):
        self.history.append((state, move))

    def end_game(self):
        if self.history:
            for state, move in self.history:
                self.update_model(state, move)
            self.save_data()
        self.history = []

class TicTacToe:
    def __init__(self, root):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.root = root
        self.ai = MarkovAI()
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
                messagebox.showinfo("Ganaste")
                self.reset()
                return
            elif is_full(self.board):
                messagebox.showinfo("Empate")
                self.reset()
                return
            self.ai_turn()

    def ai_turn(self):
        board_state = tuple(cell if cell != ' ' else '_' for row in self.board for cell in row)
        available = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == ' ']
        move = self.ai.predict_next_move(board_state, available, board=copy.deepcopy(self.board))

        if move:
            i, j = move
            self.board[i][j] = AI
            self.buttons[i][j].config(text=AI, state='disabled')

            if check_winner(self.board, AI):
                messagebox.showinfo("Perdiste")
                self.ai.end_game()
                self.reset()
            elif is_full(self.board):
                messagebox.showinfo("Empate", "¡Nadie ganó! 💤")
                self.ai.end_game()
                self.reset()

    def reset(self):
        self.ai.end_game()
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=' ', state='normal')

root = tk.Tk()
root.title("Tic Tac Toe con IA 💖")
app = TicTacToe(root)
root.mainloop()

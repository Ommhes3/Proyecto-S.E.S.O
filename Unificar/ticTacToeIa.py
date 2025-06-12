from sesoIA import MarkovAI
import json
import random
import copy
import os
import tkinter as tk
from tkinter import messagebox

from utils import check_winner, is_full, PLAYER, AI


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
root.title("Tic Tac Toe con IA ")
app = TicTacToe(root)
root.mainloop()

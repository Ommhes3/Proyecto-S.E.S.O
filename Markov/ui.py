import tkinter as tk
from game import TicTacToe
from markovModel import MarkovAI

class TicTacToeGUI:
    def __init__(self):
        # inicializar IA y ui
        self.game = TicTacToe() 
        self.ai = MarkovAI() 
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe con IA")
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.create_board()
        self.result_label = None

    def create_board(self):
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.window, text='', width=10, height=3,
                                command=lambda row=i, col=j: self.player_move(row, col))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn
        self.reset_button = tk.Button(self.window, text="Reiniciar", font=('Arial', 12), command=self.reset_game)
        self.reset_button.grid(row=4, column=0, columnspan=3, pady=10)


    def player_move(self, row, col):
        prev_state = self.game.get_board_state()  # guardar el estado antes de hacer el movimiento
        if self.game.make_move(row, col, 'X'):
            self.ai.update_model(prev_state, (row, col))  
            self.update_buttons()
            winner = self.game.check_winner()
            if winner:
                self.end_game(f"¡Ganó {winner}!")
                return
            if self.game.is_draw():
                self.end_game("¡Empate!")
                return
            self.window.after(500, self.ai_move)


    def ai_move(self):
        prev_state = self.game.get_board_state()  
        move = self.ai.get_best_move(self.game)
        self.game.make_move(*move, 'O')

        self.update_buttons()
        winner = self.game.check_winner()
        if winner:
            self.end_game(f"¡Ganó {winner}!")
        elif self.game.is_draw():
            self.end_game("¡Empate!")


    def update_buttons(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j]['text'] = self.game.board[i][j]

    def end_game(self, message):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j]['state'] = 'disabled'
        if self.result_label:
            self.result_label.destroy()
        self.result_label = tk.Label(self.window, text=message, font=('Arial', 14))
        self.result_label.grid(row=3, column=0, columnspan=3)
        
        self.ai.end_game()

    def reset_game(self):
        self.game.reset()
        for i in range(3):
            for j in range(3):
                self.buttons[i][j]['text'] = ''
                self.buttons[i][j]['state'] = 'normal'
        if self.result_label:
            self.result_label.destroy()
            self.result_label = None

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = TicTacToeGUI()
    gui.run()



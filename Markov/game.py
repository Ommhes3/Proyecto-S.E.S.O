class TicTacToe:
    
    def __init__(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]

    def reset(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]

    def make_move(self, row, col, player):
        if self.board[row][col] == '':
            self.board[row][col] = player
            return True
        return False

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] != '' and all(self.board[i][j] == self.board[i][0] for j in range(3)):
                return self.board[i][0]
            if self.board[0][i] != '' and all(self.board[j][i] == self.board[0][i] for j in range(3)):
                return self.board[0][i]
    
        if self.board[0][0] != '' and all(self.board[i][i] == self.board[0][0] for i in range(3)):
            return self.board[0][0]
        if self.board[0][2] != '' and all(self.board[i][2 - i] == self.board[0][2] for i in range(3)):
            return self.board[0][2]
        return None

    def is_draw(self):
        return all(self.board[i][j] != '' for i in range(3) for j in range(3)) and self.check_winner() is None

    def get_empty_cells(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == '']

    def get_board_state(self):
        return tuple(cell if cell != '' else '_' for row in self.board for cell in row)

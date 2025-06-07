import json
import random
import copy
import os

class MarkovAI:
    def __init__(self, data_file='markov_data.json'):
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

    def predict_next_move(self, state, available_moves):
        if state not in self.transition_counts:
            return random.choice(available_moves)

        move_counts = self.transition_counts[state]
        filtered_moves = {move: count for move, count in move_counts.items() if move in available_moves}

        if not filtered_moves:
            return random.choice(available_moves)

        total = sum(filtered_moves.values())
        moves = list(filtered_moves.keys())
        probabilities = [count / total for count in filtered_moves.values()]

        chosen_move = random.choices(moves, weights=probabilities, k=1)[0]
        return chosen_move

    def get_best_move(self, game):
        winning_move = self.check_win_block(game, 'O')
        if winning_move:
            return winning_move

        blocking_move = self.check_win_block(game, 'X')
        if blocking_move:
            return blocking_move

        state = game.get_board_state()
        return self.predict_next_move(state, game.get_empty_cells())

    def check_win_block(self, game, player):
        for move in game.get_empty_cells():
            temp_game = copy.deepcopy(game)
            temp_game.make_move(*move, player)
            if temp_game.check_winner() == player:
                return move
        return None

    def record_player_move(self, state, move):
        self.history.append((state, move))

    def end_game(self):
        for state, move in self.history:
            self.update_model(state, move)
        self.history = []
        self.save_data()


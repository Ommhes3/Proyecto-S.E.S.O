import json
import random
import copy
import os

class MarkovAI:
    def __init__(self, data_file='markov_data.json'):
        self.data_file = data_file
        self.transition_counts = {}
        self.history = [] # lista para guardar movimientos en la partida
        self.load_data() # cargar datos previos

    # funcion para cargar los datos previos desde el archivo .json
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

    # funcion para guardar nuevos datos al archivo .json
    def save_data(self):
        data = {
            str(state): {f"{k[0]},{k[1]}": v for k, v in moves.items()}
            for state, moves in self.transition_counts.items()
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)


    def update_model(self, prev_state, move):
        if prev_state not in self.transition_counts: # si el estado anterior no está registrado en el diccionario, se inicializa
            self.transition_counts[prev_state] = {}
        if move not in self.transition_counts[prev_state]: # si el movimiento desde ese estado no está registrado, se inicializa su contador
            self.transition_counts[prev_state][move] = 0
        self.transition_counts[prev_state][move] += 1 # actualiza el contador con las veces que se ha realizado ese movimiento desde ese estado

    def predict_next_move(self, state, available_moves):
        
        if state not in self.transition_counts:
            return random.choice(available_moves)

        move_counts = self.transition_counts[state] # obtener los movimientos posibles desde el estado actual

        filtered_moves = {move: count for move, count in move_counts.items() if move in available_moves} # movimientos posibles

        if not filtered_moves:
            return random.choice(available_moves)

        # Se suman las frecuencias de movimientos válidos desde el estado
        total = sum(filtered_moves.values())
        # Se extraen los movimientos válidos
        moves = list(filtered_moves.keys())
        # Se calcula la probabilidad de cada movimiento dividiendo su frecuencia entre el total de frecuencias.
        probabilities = [count / total for count in filtered_moves.values()]

        chosen_move = random.choices(moves, weights=probabilities, k=1)[0] # se selecciona un movimiento aleatorio ponderado por su probabilidad
        return chosen_move

    def get_best_move(self, game):
        # la IA revisa si puede ganar en el siguiente movimiento para colocar el O si la encuentra
        winning_move = self.check_win_block(game, 'O') 
        if winning_move:
            return winning_move

        # si no puede ganar, la IA revisa si el jugador puede ganar en el siguiente, para bloquearlo
        blocking_move = self.check_win_block(game, 'X')
        if blocking_move:
            return blocking_move

        state = game.get_board_state() # sin necesidad de bloquear o ganar, predice el sgte movimietno del jugador con markov
        return self.predict_next_move(state, game.get_empty_cells())

    # checar si puede ganar en el siguiente movimiento
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


import json
import random
import copy
import os
import tkinter as tk
from tkinter import messagebox

PLAYER = 'X'
AI = 'O'



class MarkovAI:
    def __init__(self, data_file='markov_learning.json'):
        # Establece el nombre del archivo JSON donde se guardará y cargará el conocimiento de la IA.
        self.data_file = data_file

        # Inicializa el diccionario donde se almacenarán los conteos de transiciones aprendidas.
        # Estructura: {estado_del_tablero (tuple): {movimiento (i, j): cantidad_usos}}
        self.transition_counts = {}

        # Lista para registrar los movimientos realizados durante una partida.
        # Al finalizar el juego, estos se usarán para actualizar transition_counts.
        self.history = []

        # Carga los datos previos desde el archivo JSON (si existe y es válido).
        self.load_data()

    def load_data(self):
        # Verifica si el archivo JSON existe y no está vacío.
        if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 0:
            try:
                # Abre el archivo JSON en modo lectura.
                with open(self.data_file, 'r') as f:
                    # Carga el contenido del archivo como un diccionario.
                    data = json.load(f)

                    # Convierte el contenido a la estructura interna esperada:
                    # - La clave principal (estado del tablero) se evalúa como tupla.
                    # - Las claves internas (movimientos) se convierten de string "i,j" a tupla (i, j).
                    # - Los valores representan la cantidad de veces que se ha usado ese movimiento en ese estado.
                    self.transition_counts = {
                        tuple(eval(state)): {tuple(map(int, k.split(','))): v for k, v in moves.items()}
                        for state, moves in data.items()
                    }
            except (json.JSONDecodeError, SyntaxError):
                # Si el archivo tiene un error de formato o sintaxis, se muestra un mensaje y se reinicia la memoria.
                print("Archivo JSON corrupto o mal formado, iniciando con datos vacíos.")
                self.transition_counts = {}
        else:
            # Si el archivo no existe o está vacío, se inicializa con un diccionario vacío.
            self.transition_counts = {}


    def save_data(self):
        # Convierte la estructura interna `transition_counts` en un formato serializable por JSON:
        # - Cada `state` (una tupla con el estado del tablero) se convierte a string.
        # - Cada `move` (tupla (i, j)) se convierte a string "i,j".
        # - `v` es la cantidad de veces que se ha hecho ese movimiento en ese estado.
        data = {
            str(state): {f"{k[0]},{k[1]}": v for k, v in moves.items()}
            for state, moves in self.transition_counts.items()
        }

        # Abre el archivo en modo escritura y guarda el contenido del diccionario como JSON,
        # con una indentación de 2 espacios para hacerlo legible.
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)


    def update_model(self, prev_state, move):
        # Si el estado anterior (prev_state) no está registrado en el modelo,
        # se inicializa como un nuevo diccionario vacío.
        if prev_state not in self.transition_counts:
            self.transition_counts[prev_state] = {}

        # Si el movimiento dado (move) no está registrado en ese estado,
        # se inicializa con un contador en cero.
        if move not in self.transition_counts[prev_state]:
            self.transition_counts[prev_state][move] = 0

        # Se incrementa el contador del movimiento para ese estado específico.
        # Esto representa cuántas veces se ha realizado ese movimiento en ese estado.
        self.transition_counts[prev_state][move] += 1


    def predict_next_move(self, state, available_moves, board=None):
        # Inicializa la variable del movimiento que se retornará y el origen de la decisión (para debug).
        move = None
        source = ""

        # Verifica si el estado actual existe en el modelo de transición y tiene movimientos registrados.
        if state in self.transition_counts and self.transition_counts[state]:
            move_counts = self.transition_counts[state]

            # Filtra los movimientos posibles según los disponibles en el tablero actual.
            filtered_moves = {
                move: count for move, count in move_counts.items() if move in available_moves
            }

            # Si hay movimientos filtrados válidos, se selecciona uno de forma probabilística.
            if filtered_moves:
                total = sum(filtered_moves.values())  # Suma total de ocurrencias para normalizar.
                moves = list(filtered_moves.keys())  # Lista de movimientos válidos.
                probabilities = [count / total for count in filtered_moves.values()]  # Probabilidades normalizadas.

                # Escoge aleatoriamente un movimiento basado en las probabilidades aprendidas.
                move = random.choices(moves, weights=probabilities, k=1)[0]
                source = "Markov "  # Marca que la elección fue hecha por la IA Markov.

        # Si no se encontró ningún movimiento con Markov y se proporcionó el tablero,
        # se utiliza el algoritmo Minimax para calcular el mejor movimiento.
        if move is None and board:
            move = self.get_minimax_move(board)
            if move:
                source = "Minimax "  # Marca que la elección fue hecha por Minimax.

        # Si se ha seleccionado un movimiento, se imprime el origen y se guarda en la historia para aprendizaje futuro.
        if move:
            print(f"Respuesta encontrada por {source}")
            self.record_player_move(state, move)

        # Retorna el movimiento elegido.
        return move


    def get_minimax_move(self, board):
        # Define la función recursiva interna minimax, que evalúa el valor del tablero.
        def minimax(b, is_maximizing):
            # Si gana la IA, retorna +1.
            if check_winner(b, AI): return 1
            # Si gana el jugador, retorna -1.
            if check_winner(b, PLAYER): return -1
            # Si el tablero está lleno (empate), retorna 0.
            if is_full(b): return 0

            # Si es el turno de maximizar (la IA):
            if is_maximizing:
                best = -float('inf')  # Inicializa el mejor puntaje como el menor posible.
                for i in range(3):
                    for j in range(3):
                        if b[i][j] == ' ':  # Si la celda está vacía:
                            b[i][j] = AI  # Simula el movimiento de la IA.
                            score = minimax(b, False)  # Evalúa recursivamente como minimizador.
                            b[i][j] = ' '  # Deshace el movimiento (backtracking).
                            best = max(score, best)  # Guarda el mejor puntaje posible.
                return best

            # Si es el turno de minimizar (el jugador):
            else:
                best = float('inf')  # Inicializa el mejor puntaje como el mayor posible.
                for i in range(3):
                    for j in range(3):
                        if b[i][j] == ' ':  # Si la celda está vacía:
                            b[i][j] = PLAYER  # Simula el movimiento del jugador.
                            score = minimax(b, True)  # Evalúa recursivamente como maximizador.
                            b[i][j] = ' '  # Deshace el movimiento.
                            best = min(score, best)  # Guarda el peor puntaje posible (para el jugador).
                return best

        # Inicializa las variables para encontrar el mejor movimiento.
        best_score = -float('inf')
        move = None

        # Recorre todas las posiciones posibles del tablero.
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = AI  # Simula movimiento de la IA en esa posición.
                    score = minimax(board, False)  # Evalúa la jugada usando minimax.
                    board[i][j] = ' '  # Deshace el movimiento (backtracking).

                    # Si esta jugada da mejor puntaje que las anteriores, guárdala.
                    if score > best_score:
                        best_score = score
                        move = (i, j)

        # Retorna la mejor jugada encontrada.
        return move


    def record_player_move(self, state, move):
        self.history.append((state, move))

    def end_game(self):
        if self.history:
            for state, move in self.history:
                self.update_model(state, move)
            self.save_data()
        self.history = []


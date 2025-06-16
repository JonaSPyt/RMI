import Pyro4
import threading
import json
from copy import deepcopy

TAMANHO_TABULEIRO = 5

@Pyro4.expose
class JogoSeega:
    def __init__(self):
        self.reiniciar_jogo()
        self.players = {}
        self.chat_history = []
        self.game_lock = threading.Lock()

    def reiniciar_jogo(self):
        self.tabuleiro = [['-' for _ in range(TAMANHO_TABULEIRO)] for _ in range(TAMANHO_TABULEIRO)]
        self.bloqueio_central = True
        self.inicializar_centro()
        self.fase = 1
        self.jogador_atual = 'P1'
        self.peças_p1 = 12
        self.peças_p2 = 12
        self.peças_tabuleiro_p1 = 0
        self.peças_tabuleiro_p2 = 0
        self.vencedor = None
        self.contador_colocacao = 0
        self.ultima_peça_capturadora = None

    def inicializar_centro(self):
        self.tabuleiro[2][2] = 'X' if self.bloqueio_central else '-'

    def coordenadas_validas(self, linha, coluna):
        return 0 <= linha < TAMANHO_TABULEIRO and 0 <= coluna < TAMANHO_TABULEIRO

    def connect_player(self, player_name):
        with self.game_lock:
            if len(self.players) >= 2:
                return None # Jogo cheio
            
            player_id = 'P1' if not self.players else 'P2'
            self.players[player_id] = player_name
            print(f"Jogador {player_name} conectado como {player_id}")
            return player_id

    def place_piece(self, destino, player_id):
        with self.game_lock:
            linha, coluna = destino
            if not self.coordenadas_validas(linha, coluna) or self.tabuleiro[linha][coluna] != '-' or (linha, coluna) == (2, 2):
                return False

            if self.jogador_atual != player_id or self.fase != 1:
                return False

            if player_id == 'P1' and self.peças_p1 > 0:
                self.tabuleiro[linha][coluna] = 'P'
                self.peças_p1 -= 1
                self.peças_tabuleiro_p1 += 1
                self.contador_colocacao += 1
            elif player_id == 'P2' and self.peças_p2 > 0:
                self.tabuleiro[linha][coluna] = 'B'
                self.peças_p2 -= 1
                self.peças_tabuleiro_p2 += 1
                self.contador_colocacao += 1
            else:
                return False

            if self.contador_colocacao == 2:
                self.mudar_jogador()
                self.contador_colocacao = 0

            if self.peças_p1 == 0 and self.peças_p2 == 0:
                self.fase = 2
                self.bloqueio_central = False
                self.inicializar_centro()
            return True

    def verificar_movimento_valido(self, origem, destino):
        origem_linha, origem_coluna = origem
        destino_linha, destino_coluna = destino

        if origem_linha != destino_linha and origem_coluna != destino_coluna:
            return False

        passo_linha = 0 if origem_linha == destino_linha else (1 if destino_linha > origem_linha else -1)
        passo_coluna = 0 if origem_coluna == destino_coluna else (1 if destino_coluna > origem_coluna else -1)
        
        x, y = origem_linha + passo_linha, origem_coluna + passo_coluna
        while (x, y) != (destino_linha, destino_coluna):
            if self.tabuleiro[x][y] != '-':
                return False
            x += passo_linha
            y += passo_coluna

        return self.tabuleiro[destino_linha][destino_coluna] == '-'

    def move_piece(self, origem, destino, player_id):
        with self.game_lock:
            if self.fase != 2 or self.jogador_atual != player_id:
                return False

            if not self.verificar_movimento_valido(origem, destino):
                return False

            peça = self.tabuleiro[origem[0]][origem[1]]
            self.tabuleiro[origem[0]][origem[1]] = '-'
            self.tabuleiro[destino[0]][destino[1]] = peça

            capturas = self.verificar_capturas_sanduiche(destino)
            for x, y in capturas:
                self.tabuleiro[x][y] = '-'
                if self.jogador_atual == 'P1':
                    self.peças_tabuleiro_p2 -= 1
                else:
                    self.peças_tabuleiro_p1 -= 1

            self.verificar_vencedor()
            if not capturas:
                self.mudar_jogador()
            else:
                self.ultima_peça_capturadora = destino
            return True

    def verificar_capturas_sanduiche(self, destino):
        capturas = []
        jogador = 'P' if self.jogador_atual == 'P1' else 'B'
        inimigo = 'B' if jogador == 'P' else 'P'
        direcoes = [(-1,0), (1,0), (0,-1), (0,1)]
        
        for dx, dy in direcoes:
            x, y = destino[0] + dx, destino[1] + dy
            x2, y2 = x + dx, y + dy
            if self.coordenadas_validas(x, y) and self.coordenadas_validas(x2, y2):
                if self.tabuleiro[x][y] == inimigo and self.tabuleiro[x2][y2] == jogador:
                    capturas.append((x, y))
        return capturas

    def mudar_jogador(self):
        self.jogador_atual = 'P2' if self.jogador_atual == 'P1' else 'P1'
        self.ultima_peça_capturadora = None

    def verificar_vencedor(self):
        if self.peças_tabuleiro_p1 == 0:
            self.vencedor = 'P2'
        elif self.peças_tabuleiro_p2 == 0:
            self.vencedor = 'P1'

    def send_chat_message(self, sender, message):
        with self.game_lock:
            full_message = f"{sender}: {message}"
            self.chat_history.append(full_message)
            print(f"Chat: {full_message}")

    def get_game_state(self):
        with self.game_lock:
            state = {
                'tabuleiro': self.tabuleiro,
                'jogador_atual': self.jogador_atual,
                'fase': self.fase,
                'vencedor': self.vencedor,
                'pecas_p1': self.peças_p1,
                'pecas_p2': self.peças_p2,
                'board_pieces_p1': self.peças_tabuleiro_p1,
                'board_pieces_p2': self.peças_tabuleiro_p2,
                'players': self.players
            }
            return json.dumps(state)

    def get_chat_history(self):
        with self.game_lock:
            return json.dumps(self.chat_history)

    def surrender(self, player_id):
        with self.game_lock:
            if player_id == 'P1':
                self.vencedor = 'P2'
            elif player_id == 'P2':
                self.vencedor = 'P1'
            
            player_name = self.players.get(player_id, f"Jogador {player_id}")
            surrender_message = f"{player_name} desistiu da partida!"
            self.chat_history.append(surrender_message)
            print(f"Jogador {player_id} ({player_name}) desistiu")

    def disconnect_player(self, player_id):
        with self.game_lock:
            player_name = self.players.pop(player_id, None)
            if player_name:
                print(f"Jogador {player_id} ({player_name}) desconectado")
                if self.vencedor is None and len(self.players) == 1:
                    remaining_player_id = list(self.players.keys())[0]
                    self.vencedor = remaining_player_id
                    self.chat_history.append(f"{player_name} desconectou. {self.players[remaining_player_id]} venceu!")

    def restart_game(self):
        with self.game_lock:
            self.reiniciar_jogo()
            self.chat_history.clear()
            self.chat_history.append("Nova partida iniciada!")
            print("Jogo reiniciado")


if __name__ == '__main__':
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS() # Encontra o Name Server
    uri = daemon.register(JogoSeega()) # Registra a instância do jogo
    ns.register("seega.game", uri) # Registra o objeto com um nome

    print("Servidor Seega RMI (Pyro4) pronto.")
    daemon.requestLoop() # Inicia o loop de requisições do Pyro4



import os
import numpy as np
from .mcts import Mcts, Hand
from .game import GameState
from .model import RenjuModel

class AIRunner:
    def __init__(self, config, model_path):
        self.model = RenjuModel(config)
        self.model.load(model_path)
        self.config = config
        self.restart_game()

    def restart_game(self,otherPlayerIndex = -1):
        self.game = GameState(self.config.common.game_board_size)
        self.mcts = Mcts(self.config, -otherPlayerIndex,self.model)
        self.aiplayer = -otherPlayerIndex

    def get_status(self):
        board = np.array(self.game.board)
        return {
        'board' : board.tolist(),
        'next' : self.game.playerSide,
        'finished' : self.game.finished,
        'winner' : self.game.winner,
        'debug_board' : self.game.print_beautiful()
        }

    def play(self,x,y):
        if not self.game.playerSide == -self.aiplayer : 
            return False
        if not self.game.play(x ,y):
            return False
        self.mcts.move_to_child(x,y)
        return True

    def aiplay(self):
        if not self.game.playerSide == self.aiplayer : 
            return False,Hand(0,0)
        move,_ = self.mcts.search_move(autoMoveIntoChild = False)
        if not self.game.play(move.x,move.y):
            return False,Hand(0,0)
        self.mcts.move_to_child(move.x, move.y)
        return True, move

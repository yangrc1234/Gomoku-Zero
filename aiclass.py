
from mcts import Mcts
from mcts import Hand
from gameCython import game_state
from configs.normal import EvaluateConfig as modelConfig
from model import RenjuModel
import os

import numpy as np

class AIRunner:
    def __init__(self):
        self.model = RenjuModel(modelConfig())
        self.model.load('./currentModel')
        self.config = modelConfig()
        self.restart_game()

    def restart_game(self,otherPlayerIndex = -1):
        self.game = game_state(self.config.common.game_board_size)
        self.mcts = Mcts(modelConfig(), -otherPlayerIndex,self.model)
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

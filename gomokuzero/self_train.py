from .model import RenjuModel
from .game import GameState
from .mcts import Mcts
from logging import getLogger
import logging
import json
import os
import numpy as np
import datetime
import sys

logger = getLogger(__name__)

class SelfPlay:

    def __init__(self, model_folder, play_records_folder, config):
        self.config = config
        self.play_records_folder = play_records_folder
        self.model_folder = model_folder
        self.mctsTree = None
        self.gameBoard = None
        self.bestModel = None

    def __save_game_history(self, gameHistory):
        #save file with timestamp
        if not os.path.exists(self.play_records_folder):
            os.makedirs(self.play_records_folder)
        curdate = datetime.datetime.now()
        filename = f"{curdate.year}-{curdate.month}-{curdate.day}-{curdate.hour}-{curdate.minute}-{curdate.second}-selfplay.json"
        with open(self.play_records_folder + '/' + filename,'w') as fileHandle:
            json.dump(gameHistory,fileHandle)

    def single_self_train(self):
        if self.bestModel == None:
            self.bestModel = RenjuModel.load_from_folder_or_new(self.model_folder, self.config)
        #get a mcts tree model
        self.mctsTree = [Mcts(self.config, -1, self.bestModel),Mcts(self.config, 1,self.bestModel)]
        #start a game
        gameBoard = GameState(self.config.common.game_board_size)
        #store all moves into a list.
        moveHistory = list()
        
        policyHistory = list()
        
        playerIndex = -1
        #continue the game, until player or board says no more.
        while True:
            print(gameBoard.print_beautiful() + '\n')
            sys.stdout.flush()
            mctsIndex = 0
            if playerIndex > 0 :
                mctsIndex = 1
            move,policy_ = self.mctsTree[mctsIndex].search_move(autoMoveIntoChild = False)
            if not gameBoard.play(move.x ,move.y):
                break
            moveHistory.append(move)
            policyHistory.append(policy_.tolist())
            if gameBoard.finished:
                break
            playerIndex*= -1
            for m in self.mctsTree:
                m.move_to_child(move.x,move.y)

        print(gameBoard.print_beautiful() + '\n')
        if gameBoard.finished:
            logger.warning('Game finished! The winner is ' + str(gameBoard.winner))
            gameHistory = {
                'policy' : policyHistory,
                'move' : moveHistory,
                'winner' : gameBoard.winner
            }
            self.__save_game_history(gameHistory)
        else:
            logger.warning('Game didn\' finish normally')
        #one game complete

    def self_train(self):
        while True:
            self.single_self_train()
            
def test():
    import configs.normal as mc
    t = SelfPlay(mc.MainConfig())
    t.self_train()

if __name__ == '__main__' :
    test()
from model import RenjuModel
import mcts
from .game import GameState

class Evaluator:
    def __init__(self, m1path, m2path, config):
        self.config = config
        self.m1 = RenjuModel(config)
        self.m2 = RenjuModel(config)
        self.load(m1path,m2path)

    def load(self,m1path,m2path):
        self.m1.load(m1path)
        self.m2.load(m2path)

    def test(self):
        counter = 0
        trailCount = 50
        for i in range(trailCount):
            res = self.single_versus()
            if res == None:
                trailCount -= 1
            else:
                counter += res
        print(f"Model 1 vs Model 2 with win percentage of {(-counter + trailCount) / 100}")

    def single_versus(self):
        gameBoard = GameState(self.config.common.game_board_size)
        mctsTree = [mcts.Mcts(self.config,-1,self.m1),mcts.Mcts(self.config,1,self.m2)]
        playerIndex = -1
        while True:
            print(gameBoard.print_beautiful() + '\n')
            mctsIndex = 0
            if playerIndex > 0 :
                mctsIndex = 1
            move,policy_ = mctsTree[mctsIndex].search_move(autoMoveIntoChild = False)
            if not gameBoard.play(move.x ,move.y):
                break
            if gameBoard.finished:
                break
            playerIndex*= -1
            for m in mctsTree:
                m.move_to_child(move.x,move.y)
        print(gameBoard.print_beautiful() + '\n')
        if gameBoard.finished:
            print('Game finished! The winner is ' + str(gameBoard.winner))
            return gameBoard.winner
        else:
            print('Game didn\' finish normally')

if __name__ == '__main__' :
    from .configs.normal import EvaluateConfig
    eva = Evaluator('backupModels/model2018-1-10-3-6-3','currentModel', EvaluateConfig())
    eva.test()
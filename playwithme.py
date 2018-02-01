import mcts
import configs.normal as mconfig
import gameCython
from model import RenjuModel
def test():
    conf = mconfig.EvaluateConfig()
    model = RenjuModel(conf)
    model.load('currentModel')

    while True:
        gameBoard = gameCython.game_state(conf.common.game_board_size)
        mctsTree = mcts.Mcts(conf,1,model)
        playerIndex = -1
        while True:
            print(gameBoard.print_beautiful() + '\n')

            if playerIndex < 0 :
                testerMove = input() # type: str
                xstr,ystr = testerMove.split(',')
                move = mcts.Hand(x = int(xstr) -1 ,y = int(ystr) -1)
            else:
                move,policy_ = mctsTree.search_move(autoMoveIntoChild = False)

            if not gameBoard.play(move.x ,move.y):
                break
            if gameBoard.finished:
                break
            playerIndex*= -1
            mctsTree.move_to_child(move.x,move.y)
            
        print(gameBoard.print_beautiful() + '\n')
        if gameBoard.finished:
            print('Game finished! The winner is ' + str(gameBoard.winner))
        else:
            print('Game didn\' finish normally')

if __name__ == '__main__' :
    test()
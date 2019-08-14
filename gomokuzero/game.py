import numpy as np
from enum import Enum
from collections import namedtuple

#game_state.board stores the position
#-1 means there is white, 1 is black, 0 means nothing.
class GameState: 
    def __init__(self,width, playSide = -1):
        self.width = width
        self.board = np.zeros((width,width))
        self.playerSide = playSide
        self.finished = False
        self.winner = 0

    def play(self,x,y):
        assert(not self.finished)
        if self.board[x][y] != 0:
            return False
        self.board[x][y] = self.playerSide
        self._check_renju(x,y)
        self.playerSide *= -1
        return True  

    def _check_renju(self,x,y):
        assert(self.board[x][y] != 0)
        color = self.board[x][y]
        direction = (
            (0,1),
            (1,0),
            (1,1),
            (-1,1)
        )
        def _checkBound(x,y):
            return x >= 0 and y >= 0 and x < self.width and y < self.width
        for dir in direction:
            counter = 1
            for reverse in (1,-1):
                ite = 0
                while True:
                    ite+=1
                    tp = (x + ite * dir[0] * reverse, y + ite * dir[1] * reverse)
                    if _checkBound(tp[0],tp[1]) and self.board[tp[0]][tp[1]] == color:
                        counter+= 1
                    else:
                        break
            if counter >= 5:
                self.finished=True
                self.winner = color
                break
            
    def copy(self):
        copy = GameState(self.width)
        copy.board = np.copy(self.board)
        copy.playerSide = self.playerSide
        return copy

    def print_beautiful(self):
        result = ''
        for x in range(self.width):
            for y in range(self.width):
                if self.board[x][y] == 1 :
                    result += 'x'
                if self.board[x][y] == -1:
                    result += 'o'
                if self.board[x][y] == 0:
                    result += '+'
            result += '\n'
        return result

def test():
    import configs.mini as mconfig
    testSub = GameState(mconfig.MainConfig().common.game_board_size)
    assert(testSub.playerSide == -1)
    for i in range(4):
        testSub.play(i,0)
        testSub.play(i,5)
    testSub.play(4,0)
    print(testSub.print_beautiful())

if __name__ == '__main__' :
    test()
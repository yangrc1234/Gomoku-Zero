import numpy as np
cimport numpy as np
from enum import Enum
from collections import namedtuple
from libcpp cimport bool as bool_t

DTYPE = np.int
ctypedef np.int_t DTYPE_t

#game_state.board stores the position
#-1 means there is white, 1 is black, 0 means nothing.
cdef class game_state: 
    cdef readonly int winner
    cdef readonly int boardwidth
    cdef readonly bool_t finished
    cdef readonly int playerSide
    cdef public int[:,:] board

    def __init__(self,int boardwidth,int playSide = -1):
        self.boardwidth = boardwidth
        self.board = np.zeros((boardwidth,boardwidth),dtype = DTYPE)
        self.playerSide = playSide
        self.finished = False
        self.winner = 0

    cpdef bool_t play(self,int x,int y):
        assert(not self.finished)
        if self.board[x,y] != 0:
            return False
        self.board[x,y] = self.playerSide
        self._check_renju(x,y)
        self.playerSide *= -1
        return True  

    cdef bool_t _checkBound(self, int x,int y):
        return x >= 0 and y >= 0 and x < self.boardwidth and y < self.boardwidth

    cdef void _check_renju(self,int x,int y):
        #assert(self.board[x][y] != 0)
        cdef int color = self.board[x,y]
        cdef int direction[4][2] 
        direction[0][:] = [0,1]
        direction[1][:] = [1,0]
        direction[2][:] = [1,1]
        direction[3][:] = [-1,1]

        cdef int reversement[2]
        reversement[:] = [1,-1]
        
        cdef int ite 
        cdef int counter,tx,ty
        
        cdef int reverse
        for i_dir in range(4):
            counter = 1
            for i_reverse in range(2):
                ite = 0
                reverse = reversement[i_reverse]
                while True:
                    ite+=1
                    tx = x + ite * direction[i_dir][0] * reverse
                    ty = y + ite * direction[i_dir][1] * reverse
                    if self._checkBound(tx,ty) and self.board[tx,ty] == color:
                        counter+= 1
                    else:
                        break
            if counter >= 5:
                self.finished=True
                self.winner = color
                break
            
    cpdef game_state copy(self):
        copy = game_state(self.boardwidth)
        copy.board[...] = self.board
        copy.playerSide = self.playerSide
        return copy

    def print_beautiful(self):
        result = ''
        width = self.boardwidth
        for x in range(width):
            for y in range(width):
                if self.board[x][y] == 1 :
                    result += 'o'
                if self.board[x][y] == -1:
                    result += 'x'
                if self.board[x][y] == 0:
                    result += '+'
            result += '\n'
        return result

def test():
    import configs.mini as mconfig
    testSub = game_state(mconfig.MainConfig().common.game_board_size)
    assert(testSub.playerSide == -1)
    for i in range(4):
        testSub.play(i,0)
        testSub.play(i,5)
    testSub.play(4,0)
    print(testSub.print_beautiful())

if __name__ == '__main__' :
    test()
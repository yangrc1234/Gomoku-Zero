import pstats, cProfile

import self_train
import mctsCython as mcts
import configs.mini as mconfig
import logging
import numpy as np

class mockModel():
    def __init__(self):
        pass
    def predict(self, gamestate):
        width = mconfig.CommonConfig().game_board_size
        policy = np.zeros((width,width))
        policy += 1
        policy /= width * width
        return np.resize(policy,(gamestate.shape[0],width,width)), np.resize([.1],(gamestate.shape[0]))

def selfplay_test():
    tree = self_train.SelfPlay(mconfig.MainConfig())
    for _ in range(1):
        tree.single_self_train()

def mctstest():
    mcts.test()

cProfile.runctx("selfplay_test()", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
from keras import Model
import os
import json
from collections import namedtuple
import numpy as np
import keras.callbacks as kcallback
from keras.models import load_model
import keras.backend as K
from keras.callbacks import Callback
from keras.optimizers import SGD
import shutil
from .model import RenjuModel
from .model import objective_function_for_policy, objective_function_for_value

RawData = namedtuple('RawData', ['moveHistory', 'policyHistory', 'winner'])

class Optimizer:
    def __init__(self,config,start_total_steps = 0):
        self.config = config
        self.model = None # type: RenjuModel
        self.datasets_x = list()
        self.datasets_policy = list()
        self.datasets_z = list()
        self.total_steps = start_total_steps

    def _load_raw_selfplay_records(self):
        self.datasets_x = list()
        self.datasets_policy = list()
        self.datasets_z = list()
        for filename in os.listdir('selfPlayRecords'):
            with open('selfPlayRecords/' + filename,'rb') as file:
                raw_data = json.load(file)
                typedRawData = RawData(raw_data['move'], raw_data['policy'], raw_data['winner'])
                self._flat_raw_data(typedRawData)

    def _load_model(self):
        self.model = RenjuModel(self.config)
        if os.path.exists('currentModel'):
            self.model.load('currentModel')
        else:
            self.model.build()
            self.model.save('currentModel')

    def _flat_raw_data(self,rd:RawData):
        boardWidth = self.config.common.game_board_size 
        board = np.zeros((boardWidth,boardWidth))
        player = -1
        num = len(rd.moveHistory)
        
        for i in range(num):
            for rev in (False,True):
                for rot in range(4):
                    copiedBoard = np.copy(board)
                    copiedPolicy = np.copy(rd.policyHistory[i])
                    rotatedBoard = np.rot90(copiedBoard,k = rot)
                    rotatedPolicy = np.rot90(copiedPolicy,k = rot)
                    if rev:
                        rotatedBoard = np.fliplr(rotatedBoard)
                        rotatedPolicy = np.fliplr(rotatedPolicy)
                    board1 = (rotatedBoard == player )
                    board2 = (rotatedBoard == -player)

                    self.datasets_x.append([board1,board2])
                    self.datasets_policy.append(np.reshape(rotatedPolicy,(-1)))
                    self.datasets_z.append(player*rd.winner)

            move = rd.moveHistory[i]
            board[move[0],move[1]] = player
            player *= -1

    def save_current_model(self):
        self.model.save('currentModel')

    def optimize(self, epoch=1):
        self._load_raw_selfplay_records()
        self.datasets_x = np.array(self.datasets_x)
        self.datasets_policy = np.array(self.datasets_policy)
        self.datasets_z = np.array(self.datasets_z)
        self._load_model()
        callbacks = [
            PerStepCallback(200, self.save_current_model),
        ]

        self.optimizer = SGD(lr = 1e-2,momentum=0.9)
        losses = [objective_function_for_policy, objective_function_for_value]
        self.model.model.compile(self.optimizer,losses)

        for i in range(epoch):
            print(f'Epoch : {i}')
            self.total_steps += self.train_epoch(1,callbacks)
            self.update_learning_rate(self.total_steps)

    def train_epoch(self, epochs, callbacks):
        history = self.model.model.fit(
            x=self.datasets_x,
            y=[self.datasets_policy,self.datasets_z],
            batch_size=self.config.train.batch_size,
            callbacks=callbacks,
            epochs=1,
            verbose=1
            ) # type: History
        
        steps = (self.datasets_x.shape[0] // self.config.train.batch_size) * epochs
        return steps

    def update_learning_rate(self,total_steps):
        if total_steps < 100000:
            lr = 1e-2
        elif total_steps < 200000:
            lr = 1e-3
        else:
            lr = 1e-4
        K.set_value(self.optimizer.lr,lr)

class PerStepCallback(Callback):
    def __init__(self, per_step, callback):
        super().__init__()
        self.per_step = per_step
        self.step = 0
        self.callback = callback

    def on_batch_end(self, batch, logs=None):
        self.step += 1
        if self.step % self.per_step == 0:
            self.callback()


def test():
    import configs.normal as mconfig
    Optimizer(mconfig.MainConfig()).optimize(1,300)


if __name__ == '__main__' :
    test()
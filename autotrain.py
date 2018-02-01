

import optimize
import self_train
import configs.normal as mconfig
import os
import shutil
import datetime
import time
import json

class AutoTrainer:
    def _get_timestamp(self):
        fn = datetime.datetime.now()
        return f'{fn.year}-{fn.month}-{fn.day}-{fn.hour}-{fn.minute}-{fn.second}'

    def __init__(self):
        trainedSteps = 0
        if os.path.exists('AutoTrainConfig'):
            with open('AutoTrainConfig','r') as atconfig:
                trainedSteps = json.load(atconfig)['Steps']                
        self.config = mconfig.MainConfig()
        self.sp = self_train.SelfPlay(mconfig.MainConfig())
        self.op = optimize.Optimizer(mconfig.MainConfig(),trainedSteps)

    def play(self):
        self.sp.load_model()
        if not os.path.exists('./selfPlayRecords'):
            os.mkdir('./selfPlayRecords')
        currentRecords = os.listdir('./selfPlayRecords')
        for i in range(len(currentRecords), self.config.train.max_files_num):
            self.sp.single_self_train()

    def optimize(self):
        self.op.optimize(self.config.train.iteration_epoch_count)
        with open('AutoTrainConfig','w') as atconfig:
            json.dump({'Steps' : self.op.total_steps},atconfig)
        
    def backup(self):
        if os.path.exists('currentModel'):
            shutil.copytree('currentModel','./backupModels/model' + self._get_timestamp())

    def remove_old_records(self):
        fileList = os.listdir('selfPlayRecords')
        fileList.sort(key = lambda x: os.path.getmtime('selfPlayRecords/' + x),reverse = True)
        counter = 0
        if not os.path.exists('oldSelfplay'):
            os.mkdir('oldSelfPlay')
        for i in range(self.config.train.max_files_num - self.config.train.self_play_iteration_count, len(fileList)):
            shutil.move('selfPlayRecords/' +fileList[i], 'oldSelfPlay')

    def go(self):
        while True:
            self.play()
            self.backup()
            self.optimize()
            self.remove_old_records()
            time.sleep(60)  #give this guy a rest!

if __name__ == '__main__' :
    AutoTrainer().go()
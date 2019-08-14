from gomokuzero.optimize import Optimizer
from gomokuzero.self_train import SelfPlay
import gomokuzero.configs.mini as mconfig
import os
import shutil
import datetime
import time
import json

PLAY_RECORD_FOLDER = './SelfPlayRecords'
OLD_PLAY_RECORD_FOLDER = './OldPlayRecords'
NEWEST_MODEL_FOLDER = './CurrentModel'
BACKUP_MODEL_FOLDER = './BackupModels'

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
        self.sp = SelfPlay(NEWEST_MODEL_FOLDER, PLAY_RECORD_FOLDER, self.config)
        self.op = Optimizer(self.config, PLAY_RECORD_FOLDER, NEWEST_MODEL_FOLDER, trainedSteps)

    def play(self):
        if not os.path.exists(PLAY_RECORD_FOLDER):
            os.mkdir(PLAY_RECORD_FOLDER)
        currentRecords = os.listdir(PLAY_RECORD_FOLDER)
        for i in range(len(currentRecords), self.config.train.max_files_num):
            self.sp.single_self_train()

    def optimize(self):
        self.op.optimize(self.config.train.iteration_epoch_count)
        with open('AutoTrainConfig','w') as atconfig:
            json.dump({'Steps' : self.op.total_steps},atconfig)
        
    def backup(self):
        if os.path.exists(NEWEST_MODEL_FOLDER):
            shutil.copytree(NEWEST_MODEL_FOLDER, BACKUP_MODEL_FOLDER + '/model' + self._get_timestamp())

    def remove_old_records(self):
        fileList = os.listdir(PLAY_RECORD_FOLDER)
        fileList.sort(key = lambda x: os.path.getmtime(PLAY_RECORD_FOLDER + '/' + x),reverse = True)
        if not os.path.exists(OLD_PLAY_RECORD_FOLDER):
            os.mkdir(OLD_PLAY_RECORD_FOLDER)
        for i in range(self.config.train.max_files_num - self.config.train.self_play_iteration_count, len(fileList)):
            shutil.move(PLAY_RECORD_FOLDER + '/' +fileList[i], OLD_PLAY_RECORD_FOLDER)

    def go(self):
        while True:
            self.play()
            self.backup()
            self.optimize()
            self.remove_old_records()
            time.sleep(60)  #give this guy a rest!

if __name__ == '__main__' :
    AutoTrainer().go()
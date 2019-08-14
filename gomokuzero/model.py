import hashlib
from logging import getLogger
import json
import os

import keras.backend as K
from keras.engine.topology import Input
from keras.engine.training import Model
from keras.layers.convolutional import Conv2D
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.merge import Add
from keras.layers.normalization import BatchNormalization
from keras.losses import mean_squared_error
from keras.regularizers import l2
from keras.models import load_model
from keras.optimizers import SGD
from keras.models import model_from_json

import numpy as np

logger = getLogger(__name__)

#a wrapper for Keras model.
#input a map of renju, output the move probablity and value.
#also managed to save or load from file.
class RenjuModel:

    def __init__(self, config):
        self.config = config
        self.model = None
        self.build()

    #predict a game basedon game_state.
    #the value is based on the current player. the higher, the better position the current player is in.
    def predict(self, gamestates):
        policy, value = self.model.predict(gamestates)
        return policy,value

    def build(self):
        #build the model.
        mc = self.config.model
        width = mc.input_size
        in_x = x = Input((2, width, width))  # [own(8x8), enemy(8x8)]

        # (batch, channels, height, width)
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        for _ in range(mc.res_layer_num):
            x = self._build_residual_block(x)

        res_out = x
        # for policy output
        x = Conv2D(filters=2, kernel_size=1, data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(res_out)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Flatten()(x)
        # no output for 'pass'
        policy_out = Dense(width*width, kernel_regularizer=l2(mc.l2_reg), activation="softmax", name="policy_out")(x)

        # for value output
        x = Conv2D(filters=1, kernel_size=1, data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(res_out)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Flatten()(x)
        x = Dense(mc.value_fc_size, kernel_regularizer=l2(mc.l2_reg), activation="relu")(x)
        value_out = Dense(1, kernel_regularizer=l2(mc.l2_reg), activation="tanh", name="value_out")(x)

        self.model = Model(in_x, [policy_out, value_out], name="reversi_model")

    def _build_residual_block(self, x):
        mc = self.config.model
        in_x = x
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(x)
        x = BatchNormalization(axis=1)(x)
        x = Add()([in_x, x])
        x = Activation("relu")(x)
        return x

    def save(self,path):
        if not os.path.exists(path):
            os.mkdir(path)
        self.model.save_weights(path + '/model.h5')
        model_json = self.model.to_json()
        with open(path + '/model.json', "w") as json_file:
            json_file.write(model_json)
    
    @staticmethod
    def load_from_folder_or_new(model_folder, config):
        t = RenjuModel(config)
        if os.path.exists(model_folder):
            t.load(model_folder)
        return t

    def load(self,path, old = False):
        """
        if old:
            self.model = load_model(path,custom_objects={
                "objective_function_for_policy" : objective_function_for_policy,
                "objective_function_for_value" : objective_function_for_value
            })
        else:
            json_file = open(path + '/model.json', 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            self.model = model_from_json(loaded_model_json,custom_objects={
                "objective_function_for_policy" : objective_function_for_policy,
                "objective_function_for_value" : objective_function_for_value
            })
        """
        self.model.load_weights(path + '/model.h5')
            

def objective_function_for_policy(y_true, y_pred):
    # can use categorical_crossentropy??
    return K.sum(-y_true * K.log(y_pred + K.epsilon()), axis=-1)


def objective_function_for_value(y_true, y_pred):
    return mean_squared_error(y_true, y_pred)
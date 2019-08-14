class CommonConfig:
    def __init__(self):
        self.game_board_size = 7    #keep same with below input_size

class TrainConfig:
    def __init__(self):
        self.monte_carlo_search_count = 150
        self.tau_change_step = 5
        self.c_puct = 1.0
        self.max_files_num = 100           #how many games should be stored.(older ones will get moved to oldSelfPlay)
        self.self_play_iteration_count = 20 #how many games to play for every loop.
        self.iteration_epoch_count = 5      #epoch num for every train.
        self.batch_size = 512
        self.mcts_upwrad_value_decay = 0.9  #I don't know whehter this make the AI better.

class ModelConfig:
    def __init__(self):
        self.input_size = 7
        self.cnn_filter_num = 16
        self.cnn_filter_size = 3
        self.res_layer_num = 1
        self.l2_reg = 1e-4
        self.value_fc_size = 16

class MainConfig:
    def __init__(self):
        self.model = ModelConfig()
        self.train = TrainConfig()
        self.common = CommonConfig()
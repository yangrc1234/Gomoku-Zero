class CommonConfig:
    def __init__(self):
        self.game_board_size = 9    #keep same with below input_size

class TrainConfig:
    def __init__(self):
        self.monte_carlo_search_count = 150
        self.tau_change_step = 5

class ModelConfig:
    def __init__(self):
        self.input_size = 9
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
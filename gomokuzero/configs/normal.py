class CommonConfig:
    def __init__(self):
        self.game_board_size = 11    #The game board size. Keep ModelConfig.input_size the same with this.

class TrainConfig:
    def __init__(self):
        self.monte_carlo_search_count = 400 #How many nodes will monte-carlo open during search. Higher value needs more time to compute. 400 is alpha-zero value.
        self.tau_change_step = 5            #The step when to change tau.
                                            #Before the step, ai has a chance to do stupid move.
                                            #After the step ai will always pick move with best policy value.
        self.c_puct = 1.0       #How much does the NN affets monte-carlo search.
                                #With larger value the mcts will follow NN more likely.
        self.max_files_num = 1000           #how many games should be stored.(older ones will get moved to oldSelfPlay)
        self.self_play_iteration_count = 1000 #how many games to play for every loop.
        self.iteration_epoch_count = 5      #epoch num for every train.
        self.batch_size = 512   
        self.mcts_upwrad_value_decay = 0.9  #I don't know whehter this make the AI better.

class ModelConfig:
    def __init__(self):
        self.input_size = 11
        self.cnn_filter_num = 64
        self.cnn_filter_size = 3
        self.res_layer_num = 6
        self.l2_reg = 1e-4
        self.value_fc_size = 256

#Use this when train the model.
class MainConfig:
    def __init__(self):
        self.model = ModelConfig()
        self.train = TrainConfig()
        self.common = CommonConfig()

#Use this when evaluate.
class EvaluateConfig:
    def __init__(self):
        self.model = ModelConfig()
        self.train = TrainConfig()
        self.common = CommonConfig()
        self.train.tau_change_step = -1

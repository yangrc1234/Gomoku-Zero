# cython: profile=True

from collections import defaultdict
from collections import namedtuple
from asyncio.queues import Queue
import gameCython as game
import asyncio
import math
import numpy as np

from logging import getLogger

QueueItem = namedtuple("QueueItem", "state future")

logger = getLogger(__name__)

Hand = namedtuple('Hand',['x','y'])

class MctsNode:
    def __init__(self, width):
        self.childN = np.zeros((width,width))
        self.childP = np.zeros((width,width))
        self.childW = np.zeros((width,width))
        self.childQ = np.zeros((width,width))
        self.expanded = False   #unexpanded node means just an edge.
        self.edge = defaultdict(lambda: MctsNode(width))
        self.game_board = None  #game_board will be inited once the node is created.
        self.expanding = False 

class Mcts:
    def __init__(self,config,playerIndex,model,parallelSize = 16):
        self.root_node = MctsNode(config.common.game_board_size)
        self.root_node.game_board = game.game_state(config.common.game_board_size)
        self.config = config
        self.model = model
        self.step = 0
        self.loop = asyncio.get_event_loop()
        self.playerIndex = playerIndex
        self.predictionQueue = Queue(parallelSize)
        self.searchingNodes = 0
        self.sem = asyncio.Semaphore(parallelSize)

    def get_current_game_state(self):
        return self.root_node.game_board

    def set_current_game_state(self, gamestate):
        self.root_node = MctsNode(self.config.common.game_board_size)
        self.root_node.game_board = gamestate

    def move_to_child(self, x,y):
        target = self.root_node.edge[Hand(x = x,y = y)]
        if target.game_board == None:
            target.game_board = self.root_node.game_board.copy() 
            target.game_board.play(x,y)
        self.root_node = target

    def search_move(self, autoMoveIntoChild = False):

        width = self.config.common.game_board_size

        coroutineList = list()
        for _ in range(self.config.train.monte_carlo_search_count):
            coroutineList.append(self.start_search_node(self.root_node))
        coroutineList.append(self.prediction_work())

        self.loop.run_until_complete(asyncio.gather(*coroutineList))

        #after all monte-carlo finished, back to root node, calculate policy.
        policy, raw_policy = self.calc_policy()

        if np.sum(policy) == 0:
            return Hand(0,0), raw_policy

        #now we have a policy map
        action = int(np.random.choice(range(width * width), p = policy))
        action_x = action // width
        action_y = action - action_x * width

        self.step += 1

        if autoMoveIntoChild: 
            self.move_to_child(action_x,action_y)
            
        return Hand(x = action_x,y = action_y), raw_policy.reshape((width,width))

    def calc_policy(self):
        width = self.config.common.game_board_size
        #policy_array = np.zeros(width * width)
        
        raw_policy_array = np.reshape(self.root_node.childN,(width * width))

        policy_sum = np.sum(raw_policy_array)
        if policy_sum == 0:
            return raw_policy_array,raw_policy_array
        raw_policy_array /= policy_sum

        policy_array = raw_policy_array

        if (self.step > self.config.train.tau_change_step):
            ret = np.zeros(width * width)
            ret[np.argmax(raw_policy_array)] = 1
            policy_array = ret
            
        return policy_array,raw_policy_array

    async def start_search_node(self,currentNode : MctsNode):
        self.searchingNodes += 1
        with await self.sem:
            await self.search_node(currentNode)
        self.searchingNodes -= 1

    async def search_node(self, currentNode : MctsNode):
        deltav = 0
        while currentNode.expanding:
            await asyncio.sleep(.0001)
        if not currentNode.expanded:
            currentNode.expanding = True
            deltav = await self.expand_and_evaluate(currentNode)
            currentNode.expanding = False
        else:
            edge = self.search_edge(currentNode)
            if not edge == None:
                node = currentNode.edge[edge]
                currentNode.childN[edge] += 3       #virtual loss
                if (node.game_board == None):       
                    node.game_board = currentNode.game_board.copy()      #change place?
                    node.game_board.play(edge.x,edge.y)
                deltav = await self.search_node(node)
                currentNode.childN[edge] -= 3       #virtual loss
                currentNode.childN[edge] += 1
                currentNode.childW[edge] += deltav
                currentNode.childQ[edge] = currentNode.childW[edge] / currentNode.childN[edge]
        return -deltav * self.config.train.mcts_upwrad_value_decay

    async def predict(self,x):
        narra = np.zeros(shape=(2,self.config.common.game_board_size,self.config.common.game_board_size))
        npBoard = np.array(x.board)   #make it broadcast.
        narra[0] = npBoard == x.playerSide
        narra[1] = npBoard == -x.playerSide

        future = self.loop.create_future()
        item = QueueItem(narra,future)
        await self.predictionQueue.put(item)
        return future

    async def prediction_work(self):
        await asyncio.sleep(.0001)  #avoid being the 1st to enter, and finished before others start searching.
        q = self.predictionQueue
        while self.searchingNodes > 0:
            if q.qsize() == 0:
                await asyncio.sleep(.0001)
                continue
            item_list = [q.get_nowait() for _ in range(q.qsize())]
            data = np.array([x.state for x in item_list])
            policy_a ,v_a = self.model.predict(data)
            for p, v, item in zip(policy_a, v_a, item_list):
                item.future.set_result((p, v))

    async def expand_and_evaluate(self, currentNode : MctsNode):
        #expand and evaluate the node
        #use the exisiting gameboard, run a predict, then store all move possibilities as P, return the value.
       # playedByme = -currentNode.game_board.playerSide * self.playerIndex

        if currentNode.game_board.finished:
            return -1

        currentNode.expanded=True
        future = await self.predict(currentNode.game_board)
        await future
        policy,v = future.result()

        #childP only works it currentNode isn't a terminated node.
        currentNode.childP = policy.reshape((self.config.common.game_board_size,self.config.common.game_board_size))

        #return value, so parents could get updated.
        return v
        
    def search_edge(self, currentNode : MctsNode):
        #search next node in an already expanded node
        #return None, if currentNode is terminal state.
        #a node already expanded contains all valid nodes(edges) that have gameboard.
        totalN = np.sum(currentNode.childN)
        width = self.config.common.game_board_size

        P = np.copy(currentNode.childP)
        if (currentNode == self.root_node):
            P = (1 - 0.25) * P + 0.25 * np.random.dirichlet([0.1] * width * width).reshape((width,width))
        else:
            _ = 1
            pass
        Cpuct = self.config.train.c_puct
        sqrtTotalN = max(np.sqrt(totalN),1)
        U = Cpuct * P * ( sqrtTotalN / (currentNode.childN + 1))
        
        a_ = U + 1000 # plus 1000, so that all available positions won't be 0. (otherwise, argmax will confues about illegal move and normal move) 
        #if currentNode.game_board.playerSide == self.playerIndex:
        a_ += currentNode.childQ

        legalMoves = np.array(currentNode.game_board.board) == 0
        if np.sum(legalMoves) == 0:
            return None

        a_ *= legalMoves
        #a_ is a 2d array, stores select for all hand.
        index = np.unravel_index(a_.argmax(), a_.shape)
        return Hand(x = index[0],y = index[1])

def test():
    import configs.normal as mconfig
    class mockModel():
        def __init__(self):
            pass
        def predict(self, gamestate):
            width = mconfig.CommonConfig().game_board_size
            policy = np.random.rand(width,width)
            policy /= np.sum(policy)
            
            value = np.resize([0],(gamestate.shape[0]))
            
         #   for i in range(gamestate.shape[0]):
          #      if gamestate[i][1][5][6] > 0.5:
           #         value[i] = -1

            return np.resize(policy,(gamestate.shape[0],width,width)), value
    m = mockModel()
   # import model
    #m = model.RenjuModel(mconfig.EvaluateConfig())
   # m.load('currentModel')
    #m.load('backupModels/model2018-1-9-8-26-11')
    while True:
        tm = Mcts(mconfig.EvaluateConfig(),-1,m)
        board = game.game_state(mconfig.EvaluateConfig().common.game_board_size)
        #
        for i in range(4):
            board.play(5,i)
            board.play(i * 2,3)
        #board.play(8,8)
        print(board.print_beautiful())
        tm.set_current_game_state(board)
        action,policy = tm.search_move()
        print(policy)
        print(tm.root_node.childP)
        input()
   # m.save('currentModelDir')
    
if __name__ == '__main__' :
    test()
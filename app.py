from flask import Flask
from flask import request
from gomokuzero.mcts import Mcts
from gomokuzero.game import GameState
from gomokuzero.configs.normal import EvaluateConfig as modelConfig
from gomokuzero.model import RenjuModel
from gomokuzero.aiclass import AIRunner
import json

app = Flask(__name__)
aiRunner = AIRunner(modelConfig(), './CurrentModel')

@app.route("/")
def hello():
    pass
    
@app.route('/restartGame', methods=['GET'])
def restart_game():
    ind = int(request.args['playerIndex'])
    if not (ind == 1 or ind == -1):
        return json.dumps({'status' : 'Fail'})
    aiRunner.restart_game(ind)
    return json.dumps({'status' : 'OK'})
    
@app.route('/play')
def play():
    x,y = request.args['x'],request.args['y']
    if aiRunner.play(int(x),int(y)):
        res = 'OK' 
    else :
        res = 'Fail'
    
    return json.dumps({'status' : res,'game_status' : aiRunner.get_status()})

@app.route('/aiplay')
def aiplay():
    status,move = aiRunner.aiplay()
    if (status):
        return json.dumps({'status' : 'OK', 'move' : {'x' : move.x,'y':move.y}, 'game_status' : aiRunner.get_status()})
    else:
        return json.dumps({'status':'Fail', 'game_status' : aiRunner.get_status()})

@app.route('/getGameState')
def get_game_state():
    return json.dumps(
            {
                'status' : 'OK',
                'game_status' : aiRunner.get_status()
            }
            )

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    app.run('0.0.0.0')

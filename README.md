# Gomoku-Zero
A gomoku AI based on Alpha Zero paper.  

## Requirements
* Keras  
* Tensorflow(as keras backend)  
* Flask(For browser frontend)  

requirements.txt is included in the root folder, type `pip install -r requirements.txt` in shell to auto install requirements.

## Quick Start
There's no trained model included in repo at the moment. So you need to manually train your own model.

### Auto Train
Run `python autotrain.py` to start training. Based on config, a number of games will be played during single training phase, and then all available game history will be used as training input. After the model training, some old game history will be removed.

You can configure settings in `./configs/normal.py`

### Edit Config
Config info is under `./configs/normal.py`. Most configs are commented so it's easy to understand.  

### Play with AI
Run `python playwithme.py` To start play with AI, using a ugly cmd interface.

### Play with AI in browser
If you have Flask installed, run`python app.py` and a Flask backend will start, which accepts ajax requests. 

Open `./BrowserUI/index.html`, and you can play with AI. DO NOT OPEN `localhost` or `127.0.0.1` in your browser, nothing will happen, since `app.py` is only a backend which receives requests.

If you've changed the game board size, you need to edit the var `rowNum` in line 3 of `./BrowserUI/index.js` to match your game board size during training.

## References
[1] Silver, David, et al. "Mastering the game of go without human knowledge." Nature 550.7676 (2017): 354.  
[2] [Reversi-Alpha-Zero](https://github.com/mokemokechicken/reversi-alpha-zero)

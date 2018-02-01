# Gomoku-Zero
A gomoku AI based on Alpha Zero paper.
Thanks to this great repo:
https://github.com/mokemokechicken/reversi-alpha-zero
## Requirements
Keras  
Cython  
Flask(If you need a browser frontend)
## How to use
Install all requirements above.
Run following command to generate cython file:
```
python setup.py build_ext --inplace
```
If you encounter any problem using cython, you can use game.py ,which is a pure python version with same functionality(of course, slower), to replace gameCython.py
### Auto Train
Run ``python autotrain.py`` to start training.
Based on your settings, a number of games will be played during single training phase, and then all available game history will be used as training input. After the model training, some old game history will be removed.
You can configure settings in configs/normal.py
### Play with AI
Run ``python playwithme.py`` To start play with AI, using a ugly cmd interface.
If you have Flask installed, run```python app.py``` and a Flask backend will start, which accepts ajax requests, then open AI_Five/index.html, and you can play with AI.
### Edit configs
For now, the model input is 9x9 size board. To play real gomoku game, you need to change config to 15x15, and other args as well. It will take significantly longer time to train 15x15 than 9x9.(That's why I only put a 9x9 trained model in the repo.)

## Other
### 模型保存
当前模型被放在currentModel文件夹中。训练时会自动加载该模型认为是最新模型。（不存在则会新建一个模型）  
之后训练过程中旧模型会被放到backupModels文件夹中。  
同理，selfPlayRecords保存最新的对局记录。  
旧对局记录会放到currentModel文件夹中。  
### Evaluate.py
该脚本用于衡量两个模型的实力。运行后会加载两个模型（在代码中指定），并且进行50次对局，统计胜率。  
根据alphaZero论文，alphaGo Zero中Evaluate的步骤被抛弃了。因此该脚本不被包含在自动训练的过程中。  
通过该脚本，可以观察一段时间内模型是否有进步。  
### 超参数
我们使用了一个相对非常简化的网络结构，来保证快速得到结果。  
输入层中，仅包含2层，层1表示棋盘上我方棋子，层2表示棋盘上敌方棋子。  
残差层中，每个残差块中的卷积层只包含64个卷积核（alphaZero中有256个），同时一共只有6个残差块。   
我们在评估时使用的超参数与训练（与人下或者Evaluate.py中）使用的超参数有一项变化，即tau\_change\_step，在评估时我们设置为-1，该数值本身用于添加训练集中局面的丰富程度，会让AI在前几手有概率不选择最佳走法，但是在评估时，这一做法无疑是有问题的。
### 数据增强
因为五子棋的性质，我们在训练模型时输入的训练集通过旋转、镜像进行增强；但是在对局中，我们没有对被预测的棋局进行随机旋转、镜像（因为感觉没什么用）。
### 蒙特卡洛搜索优化
在原本的代码中，我们使用的是最直接的，单线程进行蒙特卡洛搜索。这导致了在对棋局预测阶段出现性能瓶颈（频繁提交单个的预测输入）。之后我们参考reversiZero(https://github.com/mokemokechicken/reversi-alpha-zero)，将搜索修改为协程形式，模拟多线程预测。尽管协程也是单线程，但是通过将多个预测合批，性能瓶颈得到了解决。
### 神秘参数
考虑到五子棋跟围棋的不同性，我加入了一个参数`mcts_upwrad_value_decay`，在mcts搜索中向上传播时，价值会被乘上这个值。当设置为1.0时即不改变价值，即alphago的设置。  
考虑到五子棋是一招定胜负的游戏，搜索时越浅的局面，价值应该更大，因此加入了这一设置。（并没有真的去测试效果）
### 开发
该项目是ZJU软院的某课程大作业（感谢小伙伴的帮助），后续可能不会再更新。但是如果有遇到问题也可以提交issue等，我会尽力提供帮助。
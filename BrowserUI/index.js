let canvas = document.querySelector("#chessboard");
let context = canvas.getContext("2d");

let me = true; // 判断当前“我”是否有权下棋
let myColor = true; // 判断“我”的棋子的颜色
let chessBoard = []; // 棋盘二维数组，存储棋盘信息
let over = false; // 判断游戏是否结束

let rowNum = 9; // 棋盘行列数
let rowSpan = 450 / rowNum; // 每一列的宽度
let space = rowSpan / 2; // 棋盘于盒子边缘的距离

// 页面加载完成时执行
window.onload = function () {
    drawChessBoard();
};

// 开始按钮逻辑：初始化棋盘
function startGame() {
    for (let i = 0; i < rowNum; i++) {
        chessBoard[i] = [];
        for (let j = 0; j < rowNum; j++) {
            chessBoard[i][j] = 0;
        }
    }
    clearChessBoard();
    drawChessBoard();
    over = false;
    me = !document.getElementsByName("choice")[0].checked;
    myColor = !me;
    let playerIndex = me ? -1 : 1;
    document.querySelector("#start").innerHTML = "重新开始";
    accessData("restartGame", {playerIndex: playerIndex}, function (data) {
        if (data.status === "OK") {
            // 电脑落子
            accessData("aiplay", null, function (data) {
                if (data.status === "OK") {
                    drawChess(data.move.x, data.move.y, !myColor);
                    me = !me;
                }
            });
        }
    });
}

// 清除棋盘
function clearChessBoard() {
    context.fillStyle = "#FFFFFF";
    context.fillRect(0, 0, canvas.width, canvas.height);
}

// 绘制棋盘
function drawChessBoard() {
    for (let i = 0; i < rowNum; i++) {
        context.strokeStyle = "#BFBFBF";
        context.beginPath();
        context.moveTo(space + i * rowSpan, space);
        context.lineTo(space + i * rowSpan, canvas.height - space);
        context.closePath();
        context.stroke();
        context.beginPath();
        context.moveTo(space, space + i * rowSpan);
        context.lineTo(canvas.width - space, space + i * rowSpan);
        context.closePath();
        context.stroke();
    }
}

// 绘制棋子
function drawChess(i, j, me) {
    context.beginPath();
    context.arc(space + i * rowSpan, space + j * rowSpan, 13, 0, 2 * Math.PI);
    context.closePath();
    let gradient = context.createRadialGradient(space + i * rowSpan + 2, space + j * rowSpan - 2, 13, space + i * rowSpan + 2, space + j * rowSpan - 2, 0);
    if (me) {
        gradient.addColorStop(0, "#D1D1D1");
        gradient.addColorStop(1, "#F9F9F9");
    } else {
        gradient.addColorStop(0, "#0A0A0A");
        gradient.addColorStop(1, "#636766");
    }
    context.fillStyle = gradient;
    context.fill();
}

// 点击棋盘落子
canvas.onclick = function (e) {
    if (!me) return;
    if (over) return;
    let x = e.offsetX;
    let y = e.offsetY;
    let i = Math.floor(x / rowSpan);
    let j = Math.floor(y / rowSpan);
    if (chessBoard[i][j] === 0) {
        drawChess(i, j, myColor);
        chessBoard[i][j] = 1;
        accessData("play", {x: i, y: j}, function (data) {
            over = data.game_status.finished;
            if (!over) {
                me = !me;
                // 电脑落子
                accessData("aiplay", null, function (data) {
                    if (data.status === "OK") {
                        drawChess(data.move.x, data.move.y, !myColor);
                        if (data.game_status.finished) {
                            alert("游戏结束，你输了！");
                        } else {
                            me = !me;
                        }
                    }
                });
            } else {
                alert("游戏结束，你赢了！");
                me = false;
            }
        });
    }
};

// AJAX方法封装
function accessData(action, data, callback) {
    $.ajax({
        type: "GET",
        url: "http://localhost:5000/" + action,
        dataType: "JSON",
        data: data,
        success: callback,
        error: function (jqXHR) {
            alert('错误：' + jqXHR.status);
        }
    });
}
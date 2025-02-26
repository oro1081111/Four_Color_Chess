from flask import Flask, request, jsonify
from flask_cors import CORS
import copy
import time
import random
import math

# 你的 MCTS 遊戲邏輯（確保這些類別已經定義）
from MCTS import fourcolorgame, MCTSNode, mcts  # ⚠️ 這裡要替換成你的 MCTS 檔案名稱

app = Flask(__name__)
CORS(app)  # 允許跨域請求，讓前端能夠訪問後端

@app.route('/get_best_move', methods=['POST'])
def get_best_move():
    data = request.json
    board = data["board"]
    chessman = data["chessman"]
    focus = data["focus"]
    iterations = data.get("iterations", 5000)  # 預設 5000 次模擬

    print(f"AI 等級: {iterations} 次模擬")

    # 建立遊戲狀態
    game = fourcolorgame(board=board, chessman=chessman, focus=focus)
    root = MCTSNode(copy.deepcopy(game))
    
    # 執行 MCTS
    start_time = time.time()
    best_move, win_rate = mcts(root, iterations=iterations)  # 使用選擇的 AI 等級
    end_time = time.time()

    print(f"勝率 {win_rate}%, 計算時間: {round(end_time - start_time, 2)}s")

    response = {
        "best_move": best_move,
        "win_rate": win_rate,
        "compute_time": round(end_time - start_time, 2)
    }
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # 啟動 Flask 伺服器


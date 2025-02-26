
import random
import math
import copy
import time
from tqdm import tqdm


Board=[1,2,3,4,2,1,4,3,3,4,1,2,4,3,2,1]

Chessman = Board[:4] + [0] * 8 + [x + 4 for x in Board[12:16]]


class fourcolorgame:
    #棋盤、棋子、當前要移動的棋子
    def __init__(self, board=Board, chessman=Chessman, focus=1):
        self.board=board
        self.chessman=chessman
        self.focus=focus

    #當前回合玩家0或1
    def newplayer(self):
        return (self.focus-1)//4
    
    #合法移動位置
    def Legal_Action(self):
        piece_index = self.chessman.index(self.focus)
        row, col = divmod(piece_index, 4)
        movable_positions = []          
    
        # 檢查向上移動
        for r in range(row - 1, -1, -1):
            if self.chessman[r * 4 + col] != 0:
                break
            movable_positions.append(r * 4 + col)
        
        # 檢查向下移動
        for r in range(row + 1, 4):
            if self.chessman[r * 4 + col] != 0:
                break
            movable_positions.append(r * 4 + col)
        
        # 檢查向左移動
        for c in range(col - 1, -1, -1):
            if self.chessman[row * 4 + c] != 0:
                break
            movable_positions.append(row * 4 + c)
        
        # 檢查向右移動
        for c in range(col + 1, 4):
            if self.chessman[row * 4 + c] != 0:
                break
            movable_positions.append(row * 4 + c)
        return movable_positions
    
    #print出所有棋子位置
    def print_chessman(self):
        for i in range(4):
            print(self.chessman[i*4:i*4+4])
    
    #顯示當前勝利者
    def winner(self):
        if self.Legal_Action() == []:
            if self.newplayer() == 0:
                return 1
            else:
                return 0
        else:
            return None
        
    def move_piece(self, new_position):
        if new_position not in self.Legal_Action():
            print("非法移動！")
            return False  # 代表移動失敗
        piece_index = self.chessman.index(self.focus)
        self.chessman[piece_index]=0
        self.chessman[new_position]=self.focus
        if self.newplayer()==0:
            self.focus = int(self.board[new_position])+4
        else:
            self.focus = int(self.board[new_position])
        return True



class MCTSNode:
    def __init__(self, game, parent=None, move=None):
        self.game = game            # 當前遊戲狀態（複製版本）
        self.parent = parent        # 父節點
        self.move = move            # 從父節點移動到此節點所採取的走法
        self.children = []          # 子節點集合
        self.wins = 0               # 模擬勝利次數
        self.visits = 0             # 訪問次數

    def is_fully_expanded(self):
        # 當所有合法走法都已被展開則返回 True
        return len(self.children) == len(self.game.Legal_Action())

    def best_child(self, c_param=1.41):
        # 利用 UCT 值選擇最佳子節點
        choices_weights = [
            (child.wins / child.visits) + c_param * math.sqrt(2 * math.log(self.visits) / child.visits)
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]


def tree_policy(node):
    # 選擇階段：從當前節點一直往下選擇直到終局或遇到尚未完全展開的節點
    while node.game.winner() is None:
        legal_moves = node.game.Legal_Action()
        # 如果有尚未展開的走法則進行擴展
        if len(legal_moves) > len(node.children):
            return expand(node)
        else:
            node = node.best_child()
    return node


def expand(node):
    # 擴展階段：隨機選擇一個未展開的合法走法
    legal_moves = node.game.Legal_Action()
    tried_moves = [child.move for child in node.children]
    untried_moves = [move for move in legal_moves if move not in tried_moves]
    move = random.choice(untried_moves)
    
    # 複製當前遊戲狀態，並執行選擇的走法
    new_game = copy.deepcopy(node.game)
    new_game.move_piece(move)
    
    new_node = MCTSNode(new_game, parent=node, move=move)
    node.children.append(new_node)
    return new_node


def default_policy(game):
    # 模擬階段：隨機遊戲直到終局，返回勝利玩家
    while game.winner() is None:
        legal_moves = game.Legal_Action()
        if not legal_moves:
            break  # 無法移動則退出
        move = random.choice(legal_moves)
        game.move_piece(move)
    return game.winner()


def backup(node, reward):
    # 回傳階段：從當前節點向上更新勝率與訪問次數
    while node is not None:
        node.visits += 1
        # 假設 reward 表示贏家（例如 0 或 1），根據節點所屬玩家更新勝率
        # 這裡根據你的遊戲規則，贏家與節點當前玩家判斷方法可能需要調整
        if node.game.newplayer() != reward:
            node.wins += 1
        node = node.parent


def mcts(root, iterations=1000):
    # 進行多次迭代
    for i in tqdm(range(iterations)):
        # 選擇和擴展
        node = tree_policy(root)
        # 模擬：複製遊戲狀態進行隨機模擬
        simulation_game = copy.deepcopy(node.game)
        reward = default_policy(simulation_game)
        # 回傳結果更新節點
        backup(node, reward)
    # 最後選擇訪問次數最高的走法作為最佳走法
    best_kid = max(root.children, key=lambda n: n.visits)
    best_move = best_kid.move
    Win_Rate=round((100-root.wins/root.visits*100),2)
    return best_move, Win_Rate


# Game = fourcolorgame()
# root = MCTSNode(copy.deepcopy(Game))
# start_time = time.time()
# best_move, Win_Rate = mcts(root, iterations=20000)
# end_time = time.time()
# print("MCTS 選擇最佳走法:", best_move)
# print("當前勝率:", Win_Rate, "%")
# print((f"思考時間{round(end_time - start_time,2)} 秒"))


# def mcts(root, iterations=1000):
#     # 進行多次迭代
#     start_time = time.time()
#     time_list=[]
#     rate_list=[]
#     for i in tqdm(range(iterations)):
#         # 選擇和擴展
#         node = tree_policy(root)
#         # 模擬：複製遊戲狀態進行隨機模擬
#         simulation_game = copy.deepcopy(node.game)
#         reward = default_policy(simulation_game)
#         # 回傳結果更新節點
#         backup(node, reward)
#         if (i+1)%100000==0:
#             Win_Rate=round(root.wins/root.visits*100,2)
#             rate_list.append(Win_Rate)
#             end_time = time.time()
#             time_list.append(round(end_time - start_time,2))
#             start_time = time.time()
#     # 最後選擇訪問次數最高的走法作為最佳走法
#     best_kid = max(root.children, key=lambda n: n.visits)
#     best_move = best_kid.move
#     return best_move, rate_list, time_list


# 使用範例：
# 假設 Game 是已經初始化的 fourcolorgame 實例
# from your_game_module import fourcolorgame
# Game = fourcolorgame()
# root = MCTSNode(copy.deepcopy(Game))

# best_move, Rate_list, Time_list = mcts(root, iterations=1000000)
# end_time = time.time()
# print("MCTS 選擇最佳走法:", best_move)
# print(Rate_list)
# print(Time_list)
# print(Rate_list[-1],round(sum(Time_list),2))






# Game=fourcolorgame()
# Game.print_chessman()
# print(Game.focus)
# print(Game.Legal_Action())
# Game.move_piece(8)
# Game.print_chessman()
# print(Game.focus)
# print(Game.Legal_Action())
# Game.move_piece(8)

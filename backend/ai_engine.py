"""
AI 引擎 - α-β剪枝搜索、局面评估、胜率计算、推荐和推演
"""
import math
import random
from typing import Optional
from xiangqi_engine import (
    Board, Move, ROWS, COLS, EMPTY,
    RED_PIECES, BLACK_PIECES,
    PIECE_VALUES,
    R_KING, R_ADVISOR, R_ELEPHANT, R_HORSE, R_ROOK, R_CANNON, R_PAWN,
    B_KING, B_ADVISOR, B_ELEPHANT, B_HORSE, B_ROOK, B_CANNON, B_PAWN,
)

# ========== 局面评估表 ==========

# 士兵位置价值表（红方视角，黑方需翻转）
PAWN_POS_RED = [
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [20,  0, 20, 30, 40, 30, 20,  0, 20],
    [30, 40, 50, 60, 70, 60, 50, 40, 30],
    [20, 30, 40, 50, 60, 50, 40, 30, 20],
    [10, 10, 20, 30, 30, 30, 20, 10, 10],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
]

PAWN_POS_BLACK = list(reversed(PAWN_POS_RED))

# 马位置价值表
HORSE_POS_RED = [
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,  10, 20, 20, 20, 20, 20, 10,  0],
    [0,  20, 30, 40, 50, 40, 30, 20,  0],
    [0,  20, 40, 60, 70, 60, 40, 20,  0],
    [0,  10, 30, 50, 70, 50, 30, 10,  0],
    [0,  10, 20, 40, 50, 40, 20, 10,  0],
    [0,   0, 10, 20, 30, 20, 10,  0,  0],
    [0,   0,  0, 10, 10, 10,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
]
HORSE_POS_BLACK = list(reversed(HORSE_POS_RED))

# 炮位置价值表
CANNON_POS_RED = [
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,  10, 10, 10, 10, 10, 10, 10,  0],
    [0,  10, 20, 30, 30, 30, 20, 10,  0],
    [0,  10, 20, 40, 50, 40, 20, 10,  0],
    [0,  10, 20, 40, 50, 40, 20, 10,  0],
    [0,  10, 20, 30, 30, 30, 20, 10,  0],
    [0,  10, 10, 10, 10, 10, 10, 10,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
]
CANNON_POS_BLACK = list(reversed(CANNON_POS_RED))

# 车位置价值表
ROOK_POS_RED = [
    [20,  20, 10, 10, 50, 10, 10, 20,  20],
    [20,  40, 40, 50, 60, 50, 40, 40,  20],
    [10,  40, 50, 60, 70, 60, 50, 40,  10],
    [10,  50, 60, 70, 80, 70, 60, 50,  10],
    [10,  50, 60, 70, 80, 70, 60, 50,  10],
    [10,  40, 50, 60, 70, 60, 50, 40,  10],
    [10,  40, 50, 60, 70, 60, 50, 40,  10],
    [20,  40, 40, 50, 60, 50, 40, 40,  20],
    [20,  20, 20, 20, 20, 20, 20, 20,  20],
    [20,  20, 20, 20, 20, 20, 20, 20,  20],
]
ROOK_POS_BLACK = list(reversed(ROOK_POS_RED))

# 位置价值表索引
POS_TABLES = {
    'P': PAWN_POS_RED,
    'p': PAWN_POS_BLACK,
    'H': HORSE_POS_RED,
    'h': HORSE_POS_BLACK,
    'C': CANNON_POS_RED,
    'c': CANNON_POS_BLACK,
    'R': ROOK_POS_RED,
    'r': ROOK_POS_BLACK,
}

# 过河兵额外加分
PAWN_CROSSED_BONUS = 30


class AIEngine:
    """象棋 AI 引擎"""

    def __init__(self, max_depth: int = 4):
        self.max_depth = max_depth
        self.nodes_searched = 0
        self.eval_cache = {}  # 局面评估缓存
        self.transposition_table = {}  # 置换表缓存搜索结果

    def clear_cache(self):
        """清空所有缓存"""
        self.eval_cache.clear()
        self.transposition_table.clear()

    # ========== 局面评估 ==========

    def evaluate(self, board: Board) -> int:
        """
        评估局面，正分=红优，负分=黑优
        返回 centipawn 为单位的值
        """
        fen = board.to_fen()
        if fen in self.eval_cache:
            return self.eval_cache[fen]

        score = 0

        # 将死/困毙检查
        if board.game_over:
            if board.winner == 'red':
                return 100000
            elif board.winner == 'black':
                return -100000
            return 0

        for r in range(ROWS):
            for c in range(COLS):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                # 子力价值
                base_val = PIECE_VALUES[piece]
                if piece.isupper():  # 红方
                    score += base_val
                else:
                    score -= base_val

                # 位置价值
                if piece in POS_TABLES:
                    pos_bonus = POS_TABLES[piece][r][c]
                    if piece.isupper():
                        score += pos_bonus
                    else:
                        score -= pos_bonus

                # 过河兵加分
                if piece == 'P' and r < 5:
                    score += PAWN_CROSSED_BONUS
                elif piece == 'p' and r > 4:
                    score -= PAWN_CROSSED_BONUS

        # 机动性评估（简化版）
        red_mobility = len(board.generate_moves(True))
        black_mobility = len(board.generate_moves(False))
        score += (red_mobility - black_mobility) * 2

        # 将军威胁
        if board._is_king_in_check(True):
            score -= 30
        if board._is_king_in_check(False):
            score += 30

        if len(self.eval_cache) < 100000:
            self.eval_cache[fen] = score

        return score

    def win_rate(self, evaluation: int) -> dict:
        """
        将评估值转换为胜率
        使用 sigmoid 函数，保证开局对称时红黑 50:50
        """
        scale = 400  # 类似 ELO 的缩放因子

        # 基础胜率（sigmoid）
        red_win_prob = 1.0 / (1.0 + math.exp(-evaluation / scale))
        black_win_prob = 1.0 / (1.0 + math.exp(evaluation / scale))
        
        # 和棋概率：评估值越小越可能和棋
        draw_prob = 0.12 * math.exp(-(evaluation ** 2) / (2 * (scale * 0.7) ** 2))
        
        # 从胜率中扣除和棋部分
        red_win_prob = max(0.01, red_win_prob * (1.0 - draw_prob))
        black_win_prob = max(0.01, black_win_prob * (1.0 - draw_prob))
        
        # 归一化
        total = red_win_prob + draw_prob + black_win_prob
        if total > 0:
            red_win_prob /= total
            draw_prob /= total
            black_win_prob /= total

        # 判断优势方
        if evaluation > 30:
            advantage = 'red'
        elif evaluation < -30:
            advantage = 'black'
        else:
            advantage = 'equal'

        return {
            'redWinRate': round(red_win_prob * 100, 2),
            'drawRate': round(draw_prob * 100, 2),
            'blackWinRate': round(black_win_prob * 100, 2),
            'evaluation': evaluation,
            'advantage': advantage,
        }

    # ========== 搜索算法 ==========

    def _order_moves(self, moves: list[Move], board: Board) -> list[Move]:
        """走法排序（MVV-LVA + 静态评估，提高剪枝效率）"""
        move_scores = []
        for move in moves:
            score = 0
            # 1. 吃子走法优先（MVV-LVA）
            if move.captured != EMPTY:
                captured_val = PIECE_VALUES[move.captured]
                piece = board.board[move.from_row][move.from_col]
                attacker_val = PIECE_VALUES.get(piece, 0)
                score += captured_val * 100 - attacker_val
            
            # 2. 靠近中心的走法次之
            center_row, center_col = 4.5, 4
            to_dist = abs(move.to_row - center_row) + abs(move.to_col - center_col)
            from_dist = abs(move.from_row - center_row) + abs(move.from_col - center_col)
            score += (from_dist - to_dist) * 2
            
            # 3. 前进走法（对兵/卒特别重要）
            if board.red_turn:
                score += (move.from_row - move.to_row) * 5  # 向上走加分
            else:
                score += (move.to_row - move.from_row) * 5  # 向下走加分
            
            move_scores.append((score, move))
        
        # 按分数降序排列
        move_scores.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in move_scores]

    def alpha_beta(self, board: Board, depth: int, alpha: int, beta: int,
                   is_maximizing: bool) -> int:
        """α-β 剪枝搜索（带置换表优化）"""
        self.nodes_searched += 1

        # 终端节点
        if board.game_over:
            if board.winner == 'red':
                return 100000 + depth * 100
            elif board.winner == 'black':
                return -100000 - depth * 100
            return 0

        if depth == 0:
            return self.evaluate(board)

        # 置换表查找
        fen = board.to_fen()
        cache_key = f"{fen}:{depth}:{1 if is_maximizing else 0}"
        if cache_key in self.transposition_table:
            return self.transposition_table[cache_key]

        moves = board.generate_moves()
        moves = self._order_moves(moves, board)

        if not moves:
            # 无子可走
            if board._is_king_in_check(board.red_turn):
                return -100000 - depth * 100 if is_maximizing else 100000 + depth * 100
            return 0  # 困毙

        if is_maximizing:  # 红方
            max_eval = -math.inf
            for move in moves:
                new_board = board.light_copy()
                new_board._make_move_raw(move)
                eval_score = self.alpha_beta(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            # 缓存结果
            if len(self.transposition_table) < 50000:
                self.transposition_table[cache_key] = max_eval
            return max_eval
        else:  # 黑方
            min_eval = math.inf
            for move in moves:
                new_board = board.light_copy()
                new_board._make_move_raw(move)
                eval_score = self.alpha_beta(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            # 缓存结果
            if len(self.transposition_table) < 50000:
                self.transposition_table[cache_key] = min_eval
            return min_eval

    def search_best_move(self, board: Board, depth: int = None) -> tuple[Move, int]:
        """搜索最佳走法"""
        if depth is None:
            depth = self.max_depth

        self.nodes_searched = 0

        moves = board.generate_moves()
        if not moves:
            return None, 0

        moves = self._order_moves(moves, board)
        best_move = moves[0]
        best_score = -math.inf

        for move in moves:
            new_board = board.light_copy()
            new_board._make_move_raw(move)
            score = self.alpha_beta(new_board, depth - 1, -math.inf, math.inf, False)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move, best_score

    # ========== 推荐走法 ==========

    def get_recommendations(self, board: Board, top_n: int = 3,
                            depth: int = None) -> list[dict]:
        """获取 Top-N 推荐走法"""
        if depth is None:
            depth = self.max_depth

        self.nodes_searched = 0
        moves = board.generate_moves()
        if not moves:
            return []

        moves = self._order_moves(moves, board)
        results = []

        for move in moves:
            new_board = board.light_copy()
            new_board._make_move_raw(move)
            # 用深度搜索评估
            eval_score = self.alpha_beta(new_board, depth - 1, -math.inf, math.inf, False)
            win_info = self.win_rate(eval_score)

            results.append({
                'move': move.to_dict(),
                'piece': board.board[move.from_row][move.from_col],
                'evaluation': eval_score,
                'redWinRate': win_info['redWinRate'],
                'drawRate': win_info['drawRate'],
                'blackWinRate': win_info['blackWinRate'],
                'advantage': win_info['advantage'],
            })

        # 按红方胜率从高到低排序
        results.sort(key=lambda x: x['redWinRate'], reverse=True)
        return results[:top_n]

    # ========== 推演未来 ==========

    def look_ahead(self, board: Board, move: Move,
                   turns: int = 10, depth: int = 2) -> list[dict]:
        """
        推演未来的局面变化
        从当前局面执行指定走法后，模拟未来 N 回合
        返回每步后的局面信息
        
        优化：使用 depth=2 平衡速度和棋力
        """
        self.nodes_searched = 0
        sim_board = board.light_copy()
        sim_board._make_move_raw(move)

        sequence = []
        current_turn = sim_board.red_turn  # 走完 move 后的轮次

        # 第一步（用户的走法）- 使用静态评估快速返回
        eval_score = self.evaluate(sim_board)
        win_info = self.win_rate(eval_score)
        sequence.append({
            'turn': 1,
            'move': move.to_dict(),
            'board': sim_board.to_fen(),
            'redWinRate': win_info['redWinRate'],
            'drawRate': win_info['drawRate'],
            'blackWinRate': win_info['blackWinRate'],
            'isRed': True,
        })

        for t in range(2, turns + 1):
            if sim_board.game_over:
                break

            is_red = sim_board.red_turn
            # 使用 depth=2 加快推演速度
            best_move, best_score = self.search_best_move(sim_board, depth)

            if best_move is None:
                break

            sim_board._make_move_raw(best_move)
            win_info = self.win_rate(best_score)

            sequence.append({
                'turn': t,
                'move': best_move.to_dict(),
                'board': sim_board.to_fen(),
                'redWinRate': win_info['redWinRate'],
                'drawRate': win_info['drawRate'],
                'blackWinRate': win_info['blackWinRate'],
                'isRed': is_red,
            })

        return sequence

    # ========== 胜率计算 ==========

    def calculate_win_rates(self, board: Board, depth: int = None) -> dict:
        """计算当前局面双方胜率"""
        # 使用静态评估作为基准，保证对称局面左右均衡
        eval_score = self.evaluate(board)
        
        # 如果指定深度，做浅层搜索微调
        if depth and depth > 0:
            moves = board.generate_moves()
            if moves:
                best = -math.inf if board.red_turn else math.inf
                for move in moves[:8]:  # 采样前8个走法
                    new_board = board.light_copy()
                    new_board._make_move_raw(move)
                    s = self.evaluate(new_board)
                    if board.red_turn:
                        best = max(best, s)
                    else:
                        best = min(best, s)
                # 混合静态评估和搜索评估
                eval_score = int(eval_score * 0.7 + best * 0.3)
        
        return self.win_rate(eval_score)


# 创建全局引擎实例
ai_engine = AIEngine(max_depth=4)

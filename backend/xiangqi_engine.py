"""
中国象棋核心引擎 - 棋盘、走法、规则
"""
from dataclasses import dataclass
from typing import Optional
import copy
import json

# 棋盘常量
ROWS, COLS = 10, 9

# 棋子编码
EMPTY = '.'
# 红方（大写）
R_KING, R_ADVISOR, R_ELEPHANT, R_HORSE, R_ROOK, R_CANNON, R_PAWN = 'K', 'A', 'E', 'H', 'R', 'C', 'P'
# 黑方（小写）
B_KING, B_ADVISOR, B_ELEPHANT, B_HORSE, B_ROOK, B_CANNON, B_PAWN = 'k', 'a', 'e', 'h', 'r', 'c', 'p'

RED_PIECES = {R_KING, R_ADVISOR, R_ELEPHANT, R_HORSE, R_ROOK, R_CANNON, R_PAWN}
BLACK_PIECES = {B_KING, B_ADVISOR, B_ELEPHANT, B_HORSE, B_ROOK, B_CANNON, B_PAWN}

# 初始棋盘
INITIAL_BOARD = [
    list('rheakaehr'),
    list('.........'),
    list('.c.....c.'),
    list('p.p.p.p.p'),
    list('.........'),
    list('.........'),
    list('P.P.P.P.P'),
    list('.C.....C.'),
    list('.........'),
    list('RHEAKAEHR'),
]

# 棋子中文名
PIECE_NAMES = {
    'K': '帅', 'A': '仕', 'E': '相', 'H': '傌', 'R': '俥', 'C': '炮', 'P': '兵',
    'k': '将', 'a': '士', 'e': '象', 'h': '馬', 'r': '車', 'c': '砲', 'p': '卒',
}

# 棋子价值
PIECE_VALUES = {
    'K': 10000, 'A': 120, 'E': 120, 'H': 300, 'R': 600, 'C': 300, 'P': 100,
    'k': 10000, 'a': 120, 'e': 120, 'h': 300, 'r': 600, 'c': 300, 'p': 100,
}


@dataclass
class Move:
    """一步棋"""
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    captured: str = EMPTY  # 被吃掉的棋子

    def to_dict(self):
        return {
            'from': [self.from_row, self.from_col],
            'to': [self.to_row, self.to_col],
            'captured': self.captured,
            'notation': self.to_notation()
        }

    def to_notation(self):
        """转换为中文记谱"""
        piece = ''  # will be filled by caller
        fr, fc = self.from_row, self.from_col
        tr, tc = self.to_row, self.to_col
        return f"({fr},{fc})→({tr},{tc})"

    def __repr__(self):
        return f"Move({self.from_row},{self.from_col} -> {self.to_row},{self.to_col})"


class Board:
    """象棋棋盘"""

    def __init__(self, board: list = None):
        if board:
            self.board = [row[:] for row in board]
        else:
            self.board = [row[:] for row in INITIAL_BOARD]
        self.move_history: list[Move] = []
        self.position_history: list[list] = []  # 用于复盘
        self.red_turn = True  # 红方先行
        self.game_over = False
        self.winner = None  # 'red', 'black', 'draw'

    def copy(self):
        """深拷贝棋盘"""
        b = Board(self.board)
        b.red_turn = self.red_turn
        b.game_over = self.game_over
        b.winner = self.winner
        b.move_history = copy.deepcopy(self.move_history)
        b.position_history = copy.deepcopy(self.position_history)
        return b

    def light_copy(self):
        """轻量拷贝（仅棋盘+回合，不拷贝历史，用于AI搜索）"""
        b = Board.__new__(Board)
        b.board = [row[:] for row in self.board]
        b.red_turn = self.red_turn
        b.game_over = self.game_over
        b.winner = self.winner
        b.move_history = []
        b.position_history = []
        return b

    def get_piece(self, row: int, col: int) -> str:
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.board[row][col]
        return EMPTY

    def set_piece(self, row: int, col: int, piece: str):
        if 0 <= row < ROWS and 0 <= col < COLS:
            self.board[row][col] = piece

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < ROWS and 0 <= col < COLS

    def is_red(self, piece: str) -> bool:
        return piece in RED_PIECES

    def is_black(self, piece: str) -> bool:
        return piece in BLACK_PIECES

    def is_red_turn_piece(self, piece: str) -> bool:
        return (self.red_turn and self.is_red(piece)) or (not self.red_turn and self.is_black(piece))

    # ---------- 走法生成 ----------

    def _gen_king_moves(self, row: int, col: int, piece: str) -> list[Move]:
        """将/帅的走法 - 九宫内一步"""
        moves = []
        side = 'red' if self.is_red(piece) else 'black'

        # 九宫范围
        if side == 'red':
            r_range = range(7, 10)
        else:
            r_range = range(0, 3)
        c_range = range(3, 6)

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if nr in r_range and nc in c_range:
                target = self.get_piece(nr, nc)
                if target == EMPTY or (self.is_red(piece) != self.is_red(target)):
                    moves.append(Move(row, col, nr, nc, target))
        return moves

    def _gen_advisor_moves(self, row: int, col: int, piece: str) -> list[Move]:
        """仕/士的走法 - 九宫内斜走一步"""
        moves = []
        side = 'red' if self.is_red(piece) else 'black'

        if side == 'red':
            r_range = range(7, 10)
        else:
            r_range = range(0, 3)
        c_range = range(3, 6)

        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row + dr, col + dc
            if nr in r_range and nc in c_range:
                target = self.get_piece(nr, nc)
                if target == EMPTY or (self.is_red(piece) != self.is_red(target)):
                    moves.append(Move(row, col, nr, nc, target))
        return moves

    def _gen_elephant_moves(self, row: int, col: int, piece: str) -> list[Move]:
        """相/象的走法 - 田字，不能过河"""
        moves = []
        side = 'red' if self.is_red(piece) else 'black'

        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            nr, nc = row + dr, col + dc
            # 眼位
            eye_r, eye_c = row + dr // 2, col + dc // 2

            if not self.in_bounds(nr, nc):
                continue
            # 不能过河
            if side == 'red' and nr < 5:
                continue
            if side == 'black' and nr > 4:
                continue
            # 塞眼
            if self.get_piece(eye_r, eye_c) != EMPTY:
                continue

            target = self.get_piece(nr, nc)
            if target == EMPTY or (self.is_red(piece) != self.is_red(target)):
                moves.append(Move(row, col, nr, nc, target))
        return moves

    def _gen_horse_moves(self, row: int, col: int, piece: str) -> list[Move]:
        """马的走法 - 日字，蹩脚"""
        moves = []
        # 八个方向：(腿的偏移, 目标偏移)
        directions = [
            ((-1, 0), [(-2, -1), (-2, 1)]),  # 上
            ((1, 0), [(2, -1), (2, 1)]),      # 下
            ((0, -1), [(-1, -2), (1, -2)]),    # 左
            ((0, 1), [(-1, 2), (1, 2)]),       # 右
        ]

        for (leg_dr, leg_dc), targets in directions:
            leg_r, leg_c = row + leg_dr, col + leg_dc
            if not self.in_bounds(leg_r, leg_c):
                continue
            if self.get_piece(leg_r, leg_c) != EMPTY:
                continue  # 蹩马脚

            for dr, dc in targets:
                nr, nc = row + dr, col + dc
                if not self.in_bounds(nr, nc):
                    continue
                target = self.get_piece(nr, nc)
                if target == EMPTY or (self.is_red(piece) != self.is_red(target)):
                    moves.append(Move(row, col, nr, nc, target))
        return moves

    def _gen_rook_moves(self, row: int, col: int, piece: str) -> list[Move]:
        """车的走法 - 直线"""
        moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            while self.in_bounds(nr, nc):
                target = self.get_piece(nr, nc)
                if target == EMPTY:
                    moves.append(Move(row, col, nr, nc, EMPTY))
                else:
                    if self.is_red(piece) != self.is_red(target):
                        moves.append(Move(row, col, nr, nc, target))
                    break
                nr += dr
                nc += dc
        return moves

    def _gen_cannon_moves(self, row: int, col: int, piece: str) -> list[Move]:
        """炮的走法 - 直线移动 + 翻山吃子"""
        moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            # 先按车走（不吃子）
            while self.in_bounds(nr, nc):
                target = self.get_piece(nr, nc)
                if target == EMPTY:
                    moves.append(Move(row, col, nr, nc, EMPTY))
                else:
                    break  # 遇到棋子，停止前进
                nr += dr
                nc += dc

            # 再找炮架
            if self.in_bounds(nr, nc):
                # 跳过炮架
                nr += dr
                nc += dc
                while self.in_bounds(nr, nc):
                    target = self.get_piece(nr, nc)
                    if target != EMPTY:
                        if self.is_red(piece) != self.is_red(target):
                            moves.append(Move(row, col, nr, nc, target))
                        break
                    nr += dr
                    nc += dc
        return moves

    def _gen_pawn_moves(self, row: int, col: int, piece: str) -> list[Move]:
        """兵/卒的走法"""
        moves = []
        side = 'red' if self.is_red(piece) else 'black'

        if side == 'red':
            # 未过河：只能向前（上）
            forward = -1
            has_crossed = row < 5
        else:
            # 未过河：只能向前（下）
            forward = 1
            has_crossed = row > 4

        # 向前一步
        nr = row + forward
        if self.in_bounds(nr, col):
            target = self.get_piece(nr, col)
            if target == EMPTY or (self.is_red(piece) != self.is_red(target)):
                moves.append(Move(row, col, nr, col, target))

        # 过河后可以左右走
        if has_crossed:
            for dc in [-1, 1]:
                nc = col + dc
                if self.in_bounds(row, nc):
                    target = self.get_piece(row, nc)
                    if target == EMPTY or (self.is_red(piece) != self.is_red(target)):
                        moves.append(Move(row, col, row, nc, target))

        return moves

    def generate_moves(self, for_red: bool = None) -> list[Move]:
        """生成当前局面所有合法走法"""
        if for_red is None:
            for_red = self.red_turn

        raw_moves = []
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece == EMPTY:
                    continue
                if for_red and not self.is_red(piece):
                    continue
                if not for_red and not self.is_black(piece):
                    continue

                if piece.upper() == 'K':
                    raw_moves.extend(self._gen_king_moves(r, c, piece))
                elif piece.upper() == 'A':
                    raw_moves.extend(self._gen_advisor_moves(r, c, piece))
                elif piece.upper() == 'E':
                    raw_moves.extend(self._gen_elephant_moves(r, c, piece))
                elif piece.upper() == 'H':
                    raw_moves.extend(self._gen_horse_moves(r, c, piece))
                elif piece.upper() == 'R':
                    raw_moves.extend(self._gen_rook_moves(r, c, piece))
                elif piece.upper() == 'C':
                    raw_moves.extend(self._gen_cannon_moves(r, c, piece))
                elif piece.upper() == 'P':
                    raw_moves.extend(self._gen_pawn_moves(r, c, piece))

        # 过滤掉会导致己方被将的走法（使用轻量拷贝）
        legal_moves = []
        for move in raw_moves:
            new_board = self.light_copy()
            new_board._make_move_raw(move)
            if not new_board._is_king_in_check(for_red):
                legal_moves.append(move)

        return legal_moves

    def _make_move_raw(self, move: Move):
        """执行走法（不记录历史，不检查合法性）"""
        move.captured = self.board[move.to_row][move.to_col]
        self.board[move.to_row][move.to_col] = self.board[move.from_row][move.from_col]
        self.board[move.from_row][move.from_col] = EMPTY
        self.red_turn = not self.red_turn

    def make_move(self, move: Move) -> bool:
        """执行走法，返回是否合法"""
        # 验证走法合法性
        legal_moves = self.generate_moves()
        for lm in legal_moves:
            if (lm.from_row == move.from_row and lm.from_col == move.from_col and
                    lm.to_row == move.to_row and lm.to_col == move.to_col):
                # 找到合法走法
                self.position_history.append([row[:] for row in self.board])
                self.move_history.append(lm)
                self._make_move_raw(lm)
                self._check_game_end()
                return True
        return False

    def undo_move(self) -> bool:
        """悔棋"""
        if not self.position_history:
            return False
        self.board = self.position_history.pop()
        self.move_history.pop()
        self.red_turn = not self.red_turn
        self.game_over = False
        self.winner = None
        return True

    def get_board_state_at(self, move_index: int) -> list:
        """获取第 N 步后的棋盘状态"""
        if move_index < 0:
            return self.position_history[0] if self.position_history else INITIAL_BOARD
        if move_index >= len(self.position_history):
            return self.board
        return self.position_history[move_index]

    # ---------- 将军检测 ----------

    def _find_king(self, is_red: bool) -> tuple[int, int]:
        """找到将/帅的位置"""
        target = 'K' if is_red else 'k'
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] == target:
                    return r, c
        return -1, -1

    def _is_flying_general(self) -> bool:
        """检查飞将（对面笑）"""
        r_r, r_c = self._find_king(True)
        b_r, b_c = self._find_king(False)
        if r_c != b_c:
            return False
        # 同列检查中间有无棋子
        min_r, max_r = min(r_r, b_r), max(r_r, b_r)
        for r in range(min_r + 1, max_r):
            if self.board[r][r_c] != EMPTY:
                return False
        return True

    def _is_king_in_check(self, is_red: bool) -> bool:
        """检查某方是否被将军（快速版）"""
        king_r, king_c = self._find_king(is_red)
        if king_r < 0:
            return True
        return self._is_square_attacked(king_r, king_c, not is_red)

    def _is_square_attacked(self, row: int, col: int, by_red: bool) -> bool:
        """检查某个格子是否被某方攻击（快速版，不生成全部走法）"""
        # 检查将/帅（飞将）
        king_piece = 'K' if by_red else 'k'
        kr, kc = self._find_king(by_red)
        if kr >= 0 and kc == col:
            blocked = False
            min_r, max_r = min(kr, row), max(kr, row)
            for r in range(min_r + 1, max_r):
                if self.board[r][col] != EMPTY:
                    blocked = True
                    break
            if not blocked and abs(kr - row) > 0:
                return True

        # 检查车（直线）和将
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            while self.in_bounds(nr, nc):
                piece = self.board[nr][nc]
                if piece != EMPTY:
                    is_attacker_red = piece.isupper()
                    if is_attacker_red == by_red:
                        if piece.upper() == 'R':
                            return True
                        if piece.upper() == 'K' and abs(nr - row) <= 1:
                            return True
                    break
                nr += dr
                nc += dc

        # 检查马（日字+蹩脚）
        horse_offsets = [
            (-2, -1, -1, 0), (-2, 1, -1, 0),
            (2, -1, 1, 0), (2, 1, 1, 0),
            (-1, -2, 0, -1), (-1, 2, 0, 1),
            (1, -2, 0, -1), (1, 2, 0, 1),
        ]
        for dr, dc, lr, lc in horse_offsets:
            nr, nc = row + dr, col + dc
            leg_r, leg_c = row + lr, col + lc
            if self.in_bounds(nr, nc) and self.in_bounds(leg_r, leg_c):
                piece = self.board[nr][nc]
                if piece != EMPTY and ((piece.isupper() and by_red) or (piece.islower() and not by_red)):
                    if piece.upper() == 'H' and self.board[leg_r][leg_c] == EMPTY:
                        return True

        # 检查炮（翻山）
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            found_platform = False
            while self.in_bounds(nr, nc):
                piece = self.board[nr][nc]
                if not found_platform:
                    if piece != EMPTY:
                        found_platform = True
                else:
                    if piece != EMPTY:
                        is_attacker_red = piece.isupper()
                        if is_attacker_red == by_red and piece.upper() == 'C':
                            return True
                        break
                nr += dr
                nc += dc

        # 检查兵/卒（只有前方和过河后左右）
        if by_red:
            # 红方攻击者，红兵向上走
            pawn_attacks = [(-1, 0)]  # 前
            if row < 5:  # 已过河的兵可左右
                pawn_attacks.extend([(0, -1), (0, 1)])
        else:
            # 黑方攻击者，黑卒向下走
            pawn_attacks = [(1, 0)]  # 前
            if row > 4:  # 已过河的卒可左右
                pawn_attacks.extend([(0, -1), (0, 1)])

        pawn_piece = 'P' if by_red else 'p'
        for dr, dc in pawn_attacks:
            nr, nc = row + dr, col + dc
            if self.in_bounds(nr, nc) and self.board[nr][nc] == pawn_piece:
                return True

        return False

    def generate_moves_raw(self, for_red: bool) -> list[Move]:
        """生成走法（不过滤合法性，用于将军检测）"""
        moves = []
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece == EMPTY:
                    continue
                if for_red and not self.is_red(piece):
                    continue
                if not for_red and not self.is_black(piece):
                    continue

                if piece.upper() == 'K':
                    moves.extend(self._gen_king_moves(r, c, piece))
                elif piece.upper() == 'A':
                    moves.extend(self._gen_advisor_moves(r, c, piece))
                elif piece.upper() == 'E':
                    moves.extend(self._gen_elephant_moves(r, c, piece))
                elif piece.upper() == 'H':
                    moves.extend(self._gen_horse_moves(r, c, piece))
                elif piece.upper() == 'R':
                    moves.extend(self._gen_rook_moves(r, c, piece))
                elif piece.upper() == 'C':
                    moves.extend(self._gen_cannon_moves(r, c, piece))
                elif piece.upper() == 'P':
                    moves.extend(self._gen_pawn_moves(r, c, piece))
        return moves

    def is_checkmate(self, is_red: bool = None) -> bool:
        """检查是否将死（被将军且无路可逃）"""
        if is_red is None:
            is_red = self.red_turn
        # 将死 = 无合法走法 + 被将军
        return len(self.generate_moves(is_red)) == 0 and self._is_king_in_check(is_red)

    def is_stalemate(self, is_red: bool = None) -> bool:
        """检查是否困毙（无合法走法且未被将军）"""
        if is_red is None:
            is_red = self.red_turn
        return len(self.generate_moves(is_red)) == 0 and not self._is_king_in_check(is_red)

    def get_victory_type(self) -> str:
        """
        获取胜利类型
        返回: 'checkmate'(将死), 'stalemate'(困毙), 'resign'(认输), None(未结束)
        """
        if not self.game_over:
            return None
        if self.winner == 'draw':
            return 'stalemate'
        # 判断是将死还是其他胜利方式
        opponent = 'black' if self.winner == 'red' else 'red'
        opponent_is_red = (opponent == 'red')
        if self.is_checkmate(opponent_is_red):
            return 'checkmate'
        return 'resign'

    def _check_game_end(self):
        """检查游戏是否结束"""
        # 此时 red_turn 已被 _make_move_raw 翻转，当前 red_turn 指向下一个要走棋的一方
        # 需要检查当前要走棋的一方是否被将死或困毙
        current_player = self.red_turn
        if self.is_checkmate(current_player):
            # 当前要走棋的一方被将死，对方获胜
            self.game_over = True
            self.winner = 'black' if current_player else 'red'
        elif self.is_stalemate(current_player):
            self.game_over = True
            self.winner = 'draw'

    def get_check_status(self) -> dict:
        """
        获取当前将军形势状态
        返回包含以下信息的字典:
        - inCheck: 是否被将军
        - checkmateThreat: 是否有将死威胁（必赢）
        - checkingPieces: 将军的棋子列表
        - escapeMoves: 解将的走法数量
        """
        result = {
            'inCheck': False,
            'checkmateThreat': False,
            'checkingPieces': [],
            'escapeMoves': 0,
        }

        current_is_red = self.red_turn
        king_r, king_c = self._find_king(current_is_red)

        if king_r < 0:
            return result

        # 检查是否被将军
        result['inCheck'] = self._is_king_in_check(current_is_red)

        if result['inCheck']:
            # 找出将军的棋子
            result['checkingPieces'] = self._find_checking_pieces(king_r, king_c, current_is_red)
            # 计算解将走法
            legal_moves = self.generate_moves(current_is_red)
            result['escapeMoves'] = len(legal_moves)

            # 将死威胁的轻量判定：无解将走法 = 已经将死（由 _check_game_end 处理）
            # 只有1个解将走法时，快速检查对方是否能立即将死
            if result['escapeMoves'] == 1:
                result['checkmateThreat'] = self._is_checkmate_threat(current_is_red)

        return result

    def _find_checking_pieces(self, king_r: int, king_c: int, king_is_red: bool) -> list:
        """找出正在将军的棋子"""
        checking = []
        attacker_is_red = not king_is_red

        # 生成对方所有走法，看哪些能走到将的位置
        opponent_moves = self.generate_moves_raw(attacker_is_red)
        for move in opponent_moves:
            if move.to_row == king_r and move.to_col == king_c:
                piece = self.board[move.from_row][move.from_col]
                checking.append({
                    'piece': piece,
                    'from': [move.from_row, move.from_col],
                    'to': [move.to_row, move.to_col],
                })

        return checking

    def _is_checkmate_threat(self, is_red: bool) -> bool:
        """
        判断是否为将死威胁（必赢局面）
        is_red: 当前被将军的一方
        逻辑：被将军方只有1个解将走法，检查解将后对方是否能继续将死
        """
        # 获取当前所有解将走法
        escape_moves = self.generate_moves(is_red)

        for escape_move in escape_moves:
            # 模拟走解将步法
            temp_board = self.light_copy()
            temp_board._make_move_raw(escape_move)

            # 解将后轮到对方走，检查对方是否有走法能将死己方
            opponent_moves = temp_board.generate_moves(not is_red)
            for opp_move in opponent_moves[:3]:  # 只检查前3个走法，控制性能
                temp_board2 = temp_board.light_copy()
                temp_board2._make_move_raw(opp_move)

                # 对方走完后，检查己方是否被将死
                if temp_board2.is_checkmate(is_red):
                    return True

        return False

    # ---------- 导出 ----------

    def to_dict(self) -> dict:
        result = {
            'board': [''.join(row) for row in self.board],
            'redTurn': self.red_turn,
            'gameOver': self.game_over,
            'winner': self.winner,
            'moveCount': len(self.move_history),
            'moves': [m.to_dict() for m in self.move_history],
            'fen': self.to_fen()
        }
        
        # 添加胜利类型
        result['victoryType'] = self.get_victory_type()
        
        # 添加将军形势状态
        result['checkStatus'] = self.get_check_status()
        
        return result

    def to_fen(self) -> str:
        """导出 FEN 格式"""
        rows = []
        for row in self.board:
            fen_row = ''
            empty = 0
            for piece in row:
                if piece == EMPTY:
                    empty += 1
                else:
                    if empty > 0:
                        fen_row += str(empty)
                        empty = 0
                    fen_row += piece
            if empty > 0:
                fen_row += str(empty)
            rows.append(fen_row)
        turn = 'w' if self.red_turn else 'b'
        return '/'.join(rows) + ' ' + turn

    @staticmethod
    def from_fen(fen: str):
        """从 FEN 格式导入"""
        parts = fen.split()
        rows_str = parts[0].split('/')
        board = []
        for row_str in rows_str:
            row = []
            for ch in row_str:
                if ch.isdigit():
                    row.extend(['.'] * int(ch))
                else:
                    row.append(ch)
            board.append(row)
        b = Board(board)
        if len(parts) > 1:
            b.red_turn = parts[1] == 'w'
        return b

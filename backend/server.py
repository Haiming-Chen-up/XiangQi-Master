"""
FastAPI 后端服务 - 象棋教学 API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from xiangqi_engine import Board, Move, INITIAL_BOARD
from ai_engine import ai_engine

app = FastAPI(title="中国象棋教学系统", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局游戏状态
games: dict[str, Board] = {}
game_counter = 0


class MoveRequest(BaseModel):
    game_id: str
    from_row: int
    from_col: int
    to_row: int
    to_col: int


class NewGameResponse(BaseModel):
    game_id: str
    board: dict
    win_rates: dict
    recommendations: list


# ========== API 路由 ==========


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/new-game")
async def new_game():
    """创建新游戏"""
    global game_counter
    game_counter += 1
    game_id = f"game_{game_counter}"
    board = Board()
    games[game_id] = board

    win_rates = ai_engine.calculate_win_rates(board, depth=2)
    recommendations = ai_engine.get_recommendations(board, top_n=3, depth=2)

    return {
        "game_id": game_id,
        "board": board.to_dict(),
        "win_rates": win_rates,
        "recommendations": recommendations,
    }


@app.get("/api/game/{game_id}")
async def get_game(game_id: str):
    """获取游戏状态"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    win_rates = ai_engine.calculate_win_rates(board, depth=2)
    recommendations = ai_engine.get_recommendations(board, top_n=3, depth=2)

    return {
        "board": board.to_dict(),
        "win_rates": win_rates,
        "recommendations": recommendations,
    }


@app.post("/api/move")
async def make_move(req: MoveRequest):
    """用户走棋"""
    board = games.get(req.game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    if board.game_over:
        raise HTTPException(status_code=400, detail="游戏已结束")

    if not board.red_turn:
        raise HTTPException(status_code=400, detail="现在是黑方回合")

    move = Move(req.from_row, req.from_col, req.to_row, req.to_col)
    success = board.make_move(move)

    if not success:
        raise HTTPException(status_code=400, detail="非法走法")

    # 计算走棋后的局面
    win_rates = ai_engine.calculate_win_rates(board, depth=2)

    # 如果游戏没结束，AI 走黑棋
    ai_move = None
    if not board.game_over and not board.red_turn:
        best_move, best_score = ai_engine.search_best_move(board, depth=2)
        if best_move:
            board.make_move(best_move)
            ai_move = best_move.to_dict()

    # 重新计算
    win_rates = ai_engine.calculate_win_rates(board, depth=2)
    recommendations = ai_engine.get_recommendations(board, top_n=3, depth=2)

    return {
        "board": board.to_dict(),
        "win_rates": win_rates,
        "recommendations": recommendations,
        "ai_move": ai_move,
    }


@app.post("/api/ai-move")
async def ai_move_endpoint(game_id: str):
    """让 AI 走一步（黑棋）"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    if board.game_over:
        raise HTTPException(status_code=400, detail="游戏已结束")

    if board.red_turn:
        raise HTTPException(status_code=400, detail="现在是红方回合")

    best_move, best_score = ai_engine.search_best_move(board, depth=2)
    if not best_move:
        raise HTTPException(status_code=400, detail="AI 无法走棋")

    board.make_move(best_move)

    win_rates = ai_engine.calculate_win_rates(board, depth=2)
    recommendations = ai_engine.get_recommendations(board, top_n=3, depth=2)

    return {
        "board": board.to_dict(),
        "win_rates": win_rates,
        "recommendations": recommendations,
        "ai_move": best_move.to_dict(),
    }


@app.get("/api/recommendations/{game_id}")
async def get_recommendations(game_id: str):
    """获取推荐走法"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    if not board.red_turn:
        raise HTTPException(status_code=400, detail="当前不是红方回合")

    recommendations = ai_engine.get_recommendations(board, top_n=3, depth=2)
    return {"recommendations": recommendations}


@app.get("/api/legal-moves/{game_id}")
async def get_legal_moves(game_id: str, from_row: int = None, from_col: int = None):
    """获取某个棋子的合法走法，或所有合法走法"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    all_moves = board.generate_moves()

    if from_row is not None and from_col is not None:
        # 筛选指定棋子的走法
        filtered = [m.to_dict() for m in all_moves
                    if m.from_row == from_row and m.from_col == from_col]
        return {"moves": filtered}

    return {"moves": [m.to_dict() for m in all_moves]}


@app.post("/api/lookahead/{game_id}")
async def look_ahead(game_id: str, req: MoveRequest):
    """推演指定走法后的未来局面"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    move = Move(req.from_row, req.from_col, req.to_row, req.to_col)
    sequence = ai_engine.look_ahead(board, move, turns=10, depth=3)

    return {
        "sequence": sequence[:11],  # 最多10回合
        "move": move.to_dict(),
    }


@app.post("/api/undo/{game_id}")
async def undo(game_id: str):
    """悔棋（撤回用户和 AI 各一步）"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    # 悔两步（用户一步 + AI 一步）
    # 先检查当前是谁的回合
    if board.red_turn and len(board.move_history) >= 2:
        board.undo_move()  # 悔 AI 的
        board.undo_move()  # 悔用户的
    elif not board.red_turn and len(board.move_history) >= 1:
        board.undo_move()  # 悔 AI 的
    else:
        raise HTTPException(status_code=400, detail="无法悔棋")

    win_rates = ai_engine.calculate_win_rates(board, depth=2)
    recommendations = ai_engine.get_recommendations(board, top_n=3, depth=2)

    return {
        "board": board.to_dict(),
        "win_rates": win_rates,
        "recommendations": recommendations,
    }


@app.get("/api/history/{game_id}")
async def get_history(game_id: str):
    """获取走棋历史"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    moves = board.move_history
    return {
        "moves": [m.to_dict() for m in moves],
        "total": len(moves),
    }


@app.get("/api/replay/{game_id}")
async def replay(game_id: str):
    """获取复盘数据"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    history = board.position_history
    moves = board.move_history

    replay_steps = []
    for i, (pos, move) in enumerate(zip(history, moves)):
        temp_board = Board(pos)
        win_rates = ai_engine.calculate_win_rates(temp_board, depth=2)
        piece = pos[move.from_row][move.from_col]

        replay_steps.append({
            'step': i + 1,
            'board_fen': Board(pos).to_fen(),
            'move': move.to_dict(),
            'piece': piece,
            'isRed': piece.isupper(),
            'winRates': win_rates,
        })

    return {
        "steps": replay_steps,
        "total": len(replay_steps),
    }


@app.get("/api/replay-step/{game_id}/{step}")
async def replay_step(game_id: str, step: int):
    """获取复盘中的特定步骤"""
    board = games.get(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="游戏不存在")

    if step < 0 or step > len(board.position_history):
        raise HTTPException(status_code=400, detail="步骤超出范围")

    board_state = board.get_board_state_at(step)
    temp_board = Board(board_state)
    win_rates = ai_engine.calculate_win_rates(temp_board, depth=2)

    return {
        'step': step,
        'board': temp_board.to_dict(),
        'winRates': win_rates,
    }


# 静态文件服务
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')


@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, 'index.html'))


if __name__ == "__main__":
    import uvicorn
    print("🏁 中国象棋教学系统启动...")
    print(f"📂 前端目录: {frontend_dir}")
    uvicorn.run(app, host="0.0.0.0", port=8085)

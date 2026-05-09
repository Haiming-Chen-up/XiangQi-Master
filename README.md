# 🏁 中国象棋教学系统 / XiangQi Teacher

> 一个基于 FastAPI + Canvas 的人机对弈教学工具 — 边下边学，步步有据。
>
> An interactive Chinese Chess learning system. Play against an AI, understand every move.

---

## 功能 / Features

| 功能 | 说明 | Feature |
|---|---|---|
| 🎮 **人机对弈** | 用户执红棋，AI 执黑棋自动走棋 | **Human vs AI** — you play red, AI plays black |
| 📊 **实时胜率** | 每回合显示红方/和棋/黑方胜率 | **Live win rates** — red / draw / black after every move |
| 💡 **智能推荐** | 每回合推荐 3 个最佳落棋位置 | **Top-3 recommendations** — best moves ranked by evaluation |
| 🔮 **推演未来** | 点击推荐走法，查看后 10 回合棋局变化 | **Lookahead** — preview 10 turns ahead for any recommended move |
| ↩️ **悔棋** | 可撤回上一步（连同 AI 回应） | **Undo** — revert your move + AI's response (Ctrl+Z) |
| 📋 **复盘** | 逐回合回看对局过程 | **Replay** — step through the entire game move by move |

---

## 快速启动 / Quick Start

```bash
cd ~/Developer/Projects/XiangQi-Teacher
./start.sh
```

浏览器打开 / Open **http://localhost:8085**

或手动启动 / Or manually:

```bash
cd backend
pip3 install -r requirements.txt
python3 server.py
```

---

## 技术架构 / Architecture

```
XiangQi-Teacher/
├── backend/
│   ├── xiangqi_engine.py   # 棋盘引擎（走法规则、合法性校验）
│   │                       #   Board engine — rules, move validation, piece logic
│   ├── ai_engine.py        # AI 引擎（α-β剪枝、局面评估、胜率计算）
│   │                       #   AI engine — α-β pruning, position evaluation, win rates
│   └── server.py           # FastAPI 后端服务 / FastAPI REST server
├── frontend/
│   └── index.html          # 前端界面（Canvas 棋盘 + 交互面板）
│                           #   Frontend — Canvas board + interactive UI panels
└── start.sh                # 启动脚本 / Launch script
```

### AI 引擎 / AI Engine

- **α-β 剪枝搜索** — 深度可控，平衡速度与棋力
- **位置价值评估** — 各兵种（车马炮卒仕相）内置位置价值表
- **局面评分** — 综合考虑子力价值 + 位置优势 + 机动性
- **Top-N 推荐** — 排序选出最优走法，附带胜负评分

### API 端点 / API Endpoints

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/new-game` | POST | 创建新游戏 / Start new game |
| `/api/game/{id}` | GET | 获取游戏状态 / Get game state |
| `/api/move` | POST | 用户走棋 + AI 自动回应 / Make move + AI auto-reply |
| `/api/legal-moves/{id}` | GET | 获取合法走法 / Get legal moves |
| `/api/recommendations/{id}` | GET | 获取 Top-3 推荐 / Get top-3 recommendations |
| `/api/lookahead/{id}` | POST | 推演未来 10 回合 / Simulate 10 turns ahead |
| `/api/undo/{id}` | POST | 悔棋 / Undo move |
| `/api/replay/{id}` | GET | 复盘数据 / Full replay data |
| `/api/replay-step/{id}/{step}` | GET | 复盘特定步骤 / Replay specific step |

---

## 快捷键 / Shortcuts

| 按键 | 功能 |
|---|---|
| `Ctrl+Z` | 悔棋 / Undo |
| `Esc` | 取消选中 / Deselect |
| `←` `→` | 复盘/推演时前后导航 / Navigate replay & lookahead |

---

## 技术栈 / Tech Stack

| 层 | 技术 |
|---|---|
| 后端 | Python 3, FastAPI, uvicorn |
| AI | α-β 剪枝, 局面评估, 位置价值表 |
| 前端 | Vanilla HTML/CSS/JS, Canvas 2D |
| 通信 | RESTful JSON API |

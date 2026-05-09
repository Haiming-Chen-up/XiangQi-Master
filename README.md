# 🏁 中国象棋教学系统

## 功能

| 功能 | 说明 |
|---|---|
| 🎮 **人机对弈** | 用户执红棋，AI 执黑棋自动走棋 |
| 📊 **实时胜率** | 每回合显示红方/和棋/黑方胜率 |
| 💡 **智能推荐** | 每回合推荐 3 个最佳落棋位置 |
| 🔮 **推演未来** | 点击推荐走法，查看后 10 回合棋局变化 |
| ↩️ **悔棋** | 可撤回上一步（连同 AI 回应） |
| 📋 **复盘** | 逐回合回看对局过程 |

## 快速启动

```bash
cd ~/Developer/Projects/XiangQi-Teacher
./start.sh
```

浏览器打开 **http://localhost:8085**

或手动启动：

```bash
cd backend
pip3 install -r requirements.txt
python3 server.py
```

## 技术架构

```
XiangQi-Teacher/
├── backend/
│   ├── xiangqi_engine.py   # 棋盘引擎（走法规则、合法性校验）
│   ├── ai_engine.py        # AI 引擎（α-β剪枝、局面评估、胜率计算）
│   └── server.py           # FastAPI 后端服务
├── frontend/
│   └── index.html          # 前端界面（Canvas 棋盘 + 交互面板）
└── start.sh                # 启动脚本
```

### API 端点

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/new-game` | POST | 创建新游戏 |
| `/api/game/{id}` | GET | 获取游戏状态 |
| `/api/move` | POST | 用户走棋 + AI 自动回应 |
| `/api/legal-moves/{id}` | GET | 获取合法走法 |
| `/api/recommendations/{id}` | GET | 获取 Top-3 推荐 |
| `/api/lookahead/{id}` | POST | 推演未来 10 回合 |
| `/api/undo/{id}` | POST | 悔棋 |
| `/api/replay/{id}` | GET | 复盘数据 |
| `/api/replay-step/{id}/{step}` | GET | 复盘特定步骤 |

## 快捷键

| 按键 | 功能 |
|---|---|
| `Ctrl+Z` | 悔棋 |
| `Esc` | 取消选中 |

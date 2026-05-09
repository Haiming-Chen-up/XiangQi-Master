#!/bin/bash
# 中国象棋教学系统 - 启动脚本

cd "$(dirname "$0")/backend"

# 检查 Python
if ! command -v python3 &>/dev/null; then
  echo "❌ 需要 Python 3.9+"
  exit 1
fi

# 安装依赖
echo "📦 检查依赖..."
pip3 install -q fastapi uvicorn pydantic 2>/dev/null

# 启动服务
echo "🏁 中国象棋教学系统启动中..."
echo "   浏览器打开 http://localhost:8085"
python3 server.py

# 📝 贡献指南 / Contributing Guide

感谢你关注 **XiangQi-Teacher**！我们致力于打造一个智能、易用的中国象棋教学助手。请在参与贡献前花几分钟阅读以下规范。

Thank you for your interest in **XiangQi-Teacher**! We're building an intelligent Chinese Chess learning assistant. Please take a moment to read the guidelines below before contributing.

---

## 🐞 如何提交 Bug 或建议 / Reporting Bugs & Suggestions

如果你发现了 Bug 或有好的 Idea，请通过 [GitHub Issues](https://github.com/Haiming-Chen-up/XiangQi-Master/issues) 提交。

Please submit bugs or feature ideas via [GitHub Issues](https://github.com/Haiming-Chen-up/XiangQi-Master/issues).

- **搜索先行 / Search first**：提交前请先搜索已有 Issue，避免重复。Please search existing issues to avoid duplicates.
- **清晰描述 / Describe clearly**：说明问题场景、预期结果与实际结果。Describe the scenario, expected behavior, and actual behavior.
- **复现步骤 / Steps to reproduce**：提供尽可能详尽的复现步骤或截图。Provide detailed steps to reproduce, plus screenshots if possible.

---

## ⌨️ 代码规范 / Code Style

| 规范 | 约定 | Convention |
|---|---|---|
| **语言** | 后端 Python 3.12+，前端 HTML/JS | Backend Python 3.12+, Frontend HTML/JS |
| **缩进** | 统一 **4 空格**，禁用 Tab | 4 spaces only, no tabs |
| **Python 命名** | 变量/函数 `snake_case`，类 `PascalCase` | `snake_case` for vars & functions, `PascalCase` for classes |
| **JS 命名** | 变量/函数 `camelCase` | `camelCase` for variables & functions |
| **注释** | 复杂逻辑加 Docstring，README 同步更新 | Docstrings for complex logic; keep README in sync |
| **敏感信息** | 严禁提交 `.env` / API Key / 凭据 | Never commit `.env` files, API keys, or credentials |

---

## 🚀 提交 Pull Request (PR) 流程 / PR Workflow

采用 **GitHub Flow** 工作流，分为三步：

We follow **GitHub Flow** in three steps:

### 1. 同步与分支 / Sync & Branch

不要直接在 `main` 分支上开发。

Never develop directly on `main`.

```bash
# 同步上游 / Sync upstream
git checkout main
git pull origin main

# 创建特性分支 / Create feature branch
# 命名规范 / Naming: feat/功能名 或 fix/修复名
git checkout -b feat/your-awesome-feature
```

### 2. 提交与推送 / Commit & Push

```bash
# 提交前本地验证 / Test before committing
pip3 install -r backend/requirements.txt
cd backend && python3 server.py
# 浏览器打开 / Open http://localhost:8085 手动测试

# 提交 / Commit
git add .
git commit -m "feat: add your awesome feature"
git push origin feat/your-awesome-feature
```

**Commit 信息规范 / Commit Message Convention**：使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式。

| 前缀 / Prefix | 用途 / When to use |
|---|---|
| `feat:` | 新功能 / New feature |
| `fix:` | 修复 Bug / Bug fix |
| `docs:` | 文档更新 / Documentation |
| `refactor:` | 代码重构（无功能变化）/ Code restructuring |
| `style:` | 格式调整（空格、分号等）/ Formatting only |
| `test:` | 添加或修改测试 / Tests |

### 3. 发起 PR / Open a Pull Request

在 GitHub 上创建 Pull Request，从你的特性分支合并到 `main`。

Open a Pull Request on GitHub from your feature branch to `main`.

- **一个 PR 只做一件事** — 功能、修复、重构分开提。One PR, one purpose.
- **描述清楚做了什么 & 为什么** — 关联相关 Issue。Describe what and why; link related issues.
- **确保通过手动测试** — 启动服务走一遍核心流程。Make sure the core flow works manually.
- **代码审查 (Code Review)** — 维护者会 review，有意见请友好讨论。Maintainers will review; please respond constructively.

---

## 🧪 开发环境 / Dev Environment

```bash
# 克隆仓库 / Clone
git clone https://github.com/Haiming-Chen-up/XiangQi-Master.git
cd XiangQi-Teacher

# 安装依赖 / Install dependencies
pip3 install -r backend/requirements.txt

# 启动 / Start
python3 backend/server.py
# → http://localhost:8085
```

---

感谢你的贡献！每一步改进都让这个象棋老师变得更聪明 ♟️

Thanks for contributing! Every improvement makes this chess teacher a little smarter ♟️

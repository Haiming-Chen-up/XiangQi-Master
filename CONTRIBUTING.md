
# 📝 贡献指南 (Contributing Guide)

感谢你关注 **XiangQi-Master**！我们致力于打造一个智能、易用的中国象棋教学助手。为了保证项目的长期可维护性，请在参与贡献前花几分钟阅读以下规范。

---

## 🐞 如何提交 Bug 或建议
如果你发现了 Bug 或有好的 Idea，请通过 [GitHub Issues](https://github.com/Haiming-Chen-up/XiangQi-Master/issues) 提交。

*   **搜索先行**：在提交新 Issue 前，请搜索现有 Issue 确认是否已被提出。
*   **使用模板**：请清晰描述问题发生的场景、预期结果与实际结果。
*   **复现步骤**：提供尽可能详尽的复现步骤或截图。

---

## ⌨️ 代码规范
为了保持代码库的整洁，请遵循以下约定：

*   **编程语言**：后端 Python 3.12+，前端 HTML/JS。
*   **缩进风格**：统一使用 **4 个空格**，严禁使用 Tab。
*   **命名规范**：
    *   Python：变量与函数使用 `snake_case`，类名使用 `PascalCase`。
    *   JavaScript：变量与函数使用 `camelCase`。
*   **注释与文档**：复杂的逻辑必须附带 Docstring，并在 `README.md` 中更新相关的 API 或功能说明。
*   **敏感信息**：**严禁**将包含 API Key 的 `.env` 文件或个人凭据提交至仓库。

---

## 🚀 提交 Pull Request (PR) 的流程
我们采用典型的 **GitHub Flow** 工作流。请遵循以下“三板斧”：

### 1. 同步与分支
不要直接在 `main` 分支上开发。
```bash
# 先同步上游代码
git checkout main
git pull origin main

# 创建特性分支 (命名规范: feat/功能名 或 fix/修复名)
git checkout -b feat/your-awesome-feature
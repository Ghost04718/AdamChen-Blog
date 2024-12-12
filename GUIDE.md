# 鸭蛋橙🍊博客系统（Flask 简化版）


## 1. 功能需求

1. **Markdown 渲染**：支持代码高亮和 LaTeX 数学公式。

2. **标签系统**：文章按标签分类展示。

3. **搜索系统**：支持关键词全文搜索。

4. **Markdown 博客存储**：通过上传 Markdown 文件写博客，同时存储元数据到数据库。

5. **点赞和评论**：匿名用户可以点赞和评论。

6. **知识图谱页面**：展示知识关联的动态可视化图表。

7. **作品集页面**：用于展示个人项目或成果。

8. **关于我页面**：介绍个人信息和联系方式。

9. **主题风格**：清新简约，橙色为主配色。

---

## 2. 技术栈

### 后端

- **框架**：Flask（轻量化，适合小型博客）。

- Markdown 渲染：`flask-markdown`，`markdown-it-py`。

- 数据库：SQLite（开发） / PostgreSQL（生产）。

- 搜索：SQLite 全文索引（FTS）或简单 LIKE 查询。

  

### 前端

- **UI 框架**：HTML + JAVASCRIPT + CSS。

- **Markdown 渲染**：`marked.js`，代码高亮使用 `highlight.js`，LaTeX 渲染使用 KaTeX。

- **知识图谱**：`d3.js`，`vis.js`。


### 部署

- 使用 `gunicorn` 部署 Flask 应用。

- 使用 `nginx` 作为反向代理。
# 鸭蛋橙🍊博客系统

一个使用 Flask 构建的现代化个人博客系统，支持 Markdown 写作、数学公式、知识图谱等特性。专注于用户体验和内容展示，适合个人博主和技术写作者。

## ✨ 功能特点

### 📝 文章系统
- 支持 Markdown 写作，集成代码高亮
- LaTeX 数学公式渲染（支持单行 $ 和多行 $$ 语法）
- 文章标签分类和管理
- 全文搜索功能（标题和内容）
- 访问统计（总访问量、日访问量、周访问量、月访问量）
- 文章点赞和评论功能
- 文章预览和分页展示

### 🏷️ 标签系统
- 文章多标签支持
- 标签云可视化展示
- 按标签分类浏览文章
- 标签关联分析和导航

### 🗺️ 知识图谱
- 基于 D3.js 的可视化展示
- 文章和标签关联关系的动态呈现
- 支持缩放、拖拽、点击跳转等交互
- 节点悬停提示详细信息
- 智能布局和关联强度展示

### 💬 评论系统
- 访客评论功能
- 评论者信息记录
- 评论按时间倒序排列
- 评论管理和审核功能

### 🎨 作品集展示
- 个人项目展示页面
- 支持项目图片、描述、链接展示
- 项目标签分类
- 自定义项目展示顺序

### 🔍 SEO 优化
- 完整的 Meta 信息配置
- 搜索引擎友好的 URL 结构
- 文章链接永久化

### 📱 其他特性
- 响应式设计，完美支持移动端
- 深色模式支持
- 代码块一键复制
- 返回顶部按钮
- 优雅的错误页面处理

## 🚀 安装和部署

### 环境要求
- Python 3.8+
- SQLite3（默认）或 MySQL 5.7+
- 推荐使用 Linux/macOS 系统部署

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/duck-orange-blog.git
cd duck-orange-blog
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖包
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要配置
```

5. 初始化数据库
```bash
flask db upgrade
```

6. 启动应用
```bash
flask run
```

## 📝 使用指南

### 1. 管理后台

1. 访问管理后台
- 访问路径：`/admin`
- 默认账号：admin
- 默认密码：admin123
- 首次登录后请立即修改密码

2. 后台功能
- 文章管理：发布、编辑、删除文章
- 评论管理：审核、编辑、删除评论
- 标签管理：创建、编辑、删除标签
- 作品集管理：添加、编辑、删除作品

### 2. 文章管理

1. Markdown 语法支持
```markdown
# 1. 标题
# 一级标题
## 二级标题

# 2. 文本格式
**粗体文本**
*斜体文本*
> 引用文本

# 3. 代码
行内代码：`code`
代码块：
```python
def hello():
    print("Hello, World!")
```

# 4. 数学公式
行内公式：$E=mc^2$
独立公式：
$$
\frac{\partial f}{\partial x} = 2x + 2
$$

# 5. 列表
- 无序列表项
1. 有序列表项

# 6. 表格
| 表头1 | 表头2 |
|-------|-------|
| 内容1 | 内容2 |

# 7. 链接和图片
[链接文本](URL)
![图片描述](图片URL)
```

### 3. 评论管理

1. 评论功能
- 支持匿名评论
- 可选填写评论者信息
- 支持管理员审核
- 支持编辑和删除

2. 评论管理
- 在管理后台查看所有评论
- 支持按文章筛选评论
- 支持评论审核功能
- 支持删除垃圾评论

### 4. 标签管理

1. 标签使用
- 每篇文章可添加多个标签
- 标签间使用逗号分隔
- 建议每篇文章 3-5 个标签
- 使用已有标签保持一致性

2. 标签管理
- 在管理后台管理所有标签
- 支持合并相似标签
- 支持删除未使用标签
- 支持编辑标签描述

### 5. 作品集管理

1. 作品信息
- 标题：项目名称
- 描述：项目简介
- 图片：项目截图或封面
- 链接：演示地址和GitHub地址
- 标签：技术栈标签
- 排序：显示顺序

2. 作品管理
- 支持添加新作品
- 支持编辑已有作品
- 支持删除作品
- 支持调整显示顺序

### 6. 系统维护

1. 数据备份
```bash
# 备份数据库
sqlite3 app/blog.db .dump > backup.sql
```

2. 日志管理
- 日志位置：`logs/blog.log`
- 定期检查错误日志
- 及时处理异常情况

3. 安全维护
- 定期更新密码
- 检查日志中的异常访问
- 及时更新依赖包
- 定期备份重要数据

## 🎨 主题定制

1. 颜色方案配置
编辑 `app/static/css/style.css`：
```css
:root {
    --primary-color: #ff9f1c;    /* 主题色 */
    --text-color: #2d3436;       /* 文字颜色 */
    --bg-color: #ffffff;         /* 背景色 */
    --secondary-bg: #f8f9fa;     /* 次要背景色 */
}

[data-theme="dark"] {
    --primary-color: #ffd369;    /* 深色主题色 */
    --text-color: #e9ecef;       /* 深色文字颜色 */
    --bg-color: #222831;         /* 深色背景色 */
    --secondary-bg: #393e46;     /* 深色次要背景色 */
}
```

## 📄 许可证

MIT License

## 🙏 技术栈

- 后端：Flask + SQLAlchemy
- 前端：HTML5 + CSS3 + JavaScript
- 可视化：D3.js
- 扩展：Python-Markdown + KaTeX

## 📞 技术支持

- 问题反馈：https://github.com/yourusername/duck-orange-blog/issues
```

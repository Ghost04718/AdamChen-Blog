import click
from flask.cli import with_appcontext
from app import db
from app.models import Post, Tag, Comment, Portfolio
from datetime import datetime
import os
import shutil

def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_sample_data)
    app.cli.add_command(backup_db_command)
    app.cli.add_command(add_portfolio_command)
    app.cli.add_command(batch_add_portfolio_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """初始化数据库表"""
    # 检查是否已存在表
    if not db.engine.has_table('post'):
        db.create_all()
        click.echo('数据库初始化完成.')
    else:
        click.echo('数据库表已存在，跳过初始化.')

@click.command('create-sample')
@with_appcontext
def create_sample_data():
    """创建示例数据"""
    # 检查是否已有数据
    if Post.query.first() is not None:
        click.echo('数据库中已有数据，跳过示例数据创建.')
        return

    # 创建示例标签
    tags = [
        Tag(name='Python'),
        Tag(name='Flask'),
        Tag(name='Web开发'),
        Tag(name='数据库'),
        Tag(name='前端')
    ]
    for tag in tags:
        db.session.add(tag)
    
    # 创建示例文章
    posts = [
        Post(
            title='Flask博客系统开发教程',
            content='''
# Flask博客系统开发教程

这是一篇关于如何使用Flask开发博客系统的教程。

## 主要特性

- Markdown支持
- 标签系统
- 评论功能
- 访问统计

## 技术栈

- Flask
- SQLAlchemy
- Bootstrap
- jQuery
            ''',
            created_at=datetime.utcnow(),
            tags=[tags[0], tags[1], tags[2]]
        ),
        Post(
            title='Web前端开发基础',
            content='''
# Web前端开发基础

前端开发的基础知识介绍。

## 核心技术

- HTML5
- CSS3
- JavaScript

## 进阶内容

- Vue.js
- React
- TypeScript
            ''',
            created_at=datetime.utcnow(),
            tags=[tags[4]]
        )
    ]
    for post in posts:
        db.session.add(post)
    
    # 创建示例作品集
    portfolios = [
        Portfolio(
            title='个人博客系统',
            description='使用Flask开发的个人博客系统',
            image_url='/static/images/portfolio/blog.jpg',
            project_url='https://github.com/example/blog',
            github_url='https://github.com/example/blog',
            tags='Python,Flask,SQLAlchemy',
            order=1
        ),
        Portfolio(
            title='知识图谱可视化',
            description='基于D3.js的知识图谱可视化项目',
            image_url='/static/images/portfolio/graph.jpg',
            project_url='https://github.com/example/knowledge-graph',
            github_url='https://github.com/example/knowledge-graph',
            tags='JavaScript,D3.js,数据可视化',
            order=2
        )
    ]
    for portfolio in portfolios:
        db.session.add(portfolio)
    
    try:
        db.session.commit()
        click.echo('示例数据创建成功.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'创建示例数据失败: {str(e)}') 

@click.command('backup-db')
@with_appcontext
def backup_db_command():
    """备份数据库"""
    # 创建备份目录
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'blog_{timestamp}.db')
    
    try:
        # 复制数据库文件
        shutil.copy2('blog.db', backup_file)
        click.echo(f'数据库备份成功: {backup_file}')
    except Exception as e:
        click.echo(f'备份失败: {str(e)}') 

@click.command('add-portfolio')
@click.argument('title')
@click.argument('description')
@click.argument('image_path', required=False)
@click.option('--project-url', default=None, help='项目演示链接')
@click.option('--github-url', default=None, help='GitHub仓库链接')
@click.option('--tags', default='', help='标签，用逗号分隔')
@click.option('--order', default=0, help='排序顺序，数字越小越靠前')
@with_appcontext
def add_portfolio_command(title, description, image_path, project_url, github_url, tags, order):
    """添加新的作品集项目"""
    try:
        # 处理图片
        image_url = None
        if image_path and os.path.exists(image_path):
            # 确保目标目录存在
            upload_folder = os.path.join('app', 'static', 'images', 'portfolio')
            os.makedirs(upload_folder, exist_ok=True)
            
            # 生成唯一的文件名
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(image_path)}"
            destination = os.path.join(upload_folder, filename)
            
            # 复制图片到目标目录
            shutil.copy2(image_path, destination)
            
            # 设置相对URL路径
            image_url = f"/static/images/portfolio/{filename}"

        # 创建作品集记录
        portfolio = Portfolio(
            title=title,
            description=description,
            image_url=image_url,
            project_url=project_url,
            github_url=github_url,
            tags=tags,
            order=order
        )
        
        db.session.add(portfolio)
        db.session.commit()
        
        click.echo(f'成功添加作品: {title}')
        if image_url:
            click.echo(f'图片已保存到: {image_url}')
            
    except Exception as e:
        click.echo(f'添加作品失败: {str(e)}', err=True)
        db.session.rollback()

@click.command('batch-add-portfolio')
@click.argument('json_file')
@with_appcontext
def batch_add_portfolio_command(json_file):
    """从JSON文件批量添加作品集项目"""
    import json
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            projects = json.load(f)
        
        for project in projects:
            try:
                # 处理图片
                image_url = None
                if 'image_path' in project and os.path.exists(project['image_path']):
                    upload_folder = os.path.join('app', 'static', 'images', 'portfolio')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(project['image_path'])}"
                    destination = os.path.join(upload_folder, filename)
                    
                    shutil.copy2(project['image_path'], destination)
                    image_url = f"/static/images/portfolio/{filename}"

                # 创建作品集记录
                portfolio = Portfolio(
                    title=project['title'],
                    description=project['description'],
                    image_url=image_url,
                    project_url=project.get('project_url'),
                    github_url=project.get('github_url'),
                    tags=project.get('tags', ''),
                    order=project.get('order', 0)
                )
                
                db.session.add(portfolio)
                click.echo(f'添加作品: {project["title"]}')
                
            except Exception as e:
                click.echo(f'添加作品 {project.get("title", "未知")} 失败: {str(e)}', err=True)
                continue
        
        db.session.commit()
        click.echo('批量添加作品完成')
        
    except Exception as e:
        click.echo(f'批量添加作品失败: {str(e)}', err=True)
        db.session.rollback()
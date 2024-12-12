from flask import Blueprint, render_template, request, jsonify, redirect, url_for, Markup, make_response, current_app, session
from app.models import Post, Comment, Portfolio, Tag
from app import db
import markdown
from mdx_math import MathExtension
from datetime import date, timedelta, datetime
from collections import defaultdict

main = Blueprint('main', __name__)

def md_to_html(content):
    extensions = [
        'fenced_code',
        'codehilite',
        'tables',
        MathExtension(enable_dollar_delimiter=True),
        'meta',
        'nl2br'
    ]
    extension_configs = {
        'mdx_math': {
            'enable_dollar_delimiter': True,
            'add_preview': True
        }
    }
    md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
    return Markup(md.convert(content))

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    for post in posts.items:
        post.preview = md_to_html(post.content[:200] + '...' if len(post.content) > 200 else post.content)
    
    # 侧栏数据
    total_posts = Post.query.count()
    total_tags = Tag.query.count()
    total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
    
    # 最近文章
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    # 标签云数据
    tags = Tag.query.all()
    tag_counts = {tag.name: tag.posts.count() for tag in tags}
    max_count = max(tag_counts.values()) if tag_counts else 1
    
    return render_template('index.html', 
                         posts=posts,
                         total_posts=total_posts,
                         total_tags=total_tags,
                         total_views=total_views,
                         recent_posts=recent_posts,
                         tags=tag_counts,
                         max_count=max_count)

@main.route('/post/<int:post_id>')
def post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        current_app.logger.info(f'Viewing post {post_id}', 
                              extra={'ip': request.remote_addr})
        
        # 更新访问统计
        today = date.today()
        if post.last_view_date != today:
            post.daily_views = 0
            if today.weekday() == 0:
                post.weekly_views = 0
            if today.day == 1:
                post.monthly_views = 0
        
        post.views += 1
        post.daily_views += 1
        post.weekly_views += 1
        post.monthly_views += 1
        post.last_view_date = today
        try:  # 添加内部事务处理
            db.session.commit()
        except:
            db.session.rollback()
            # 访问统计失败不应影响页面显示
        
        post.html_content = md_to_html(post.content)
        post.comments = post.comments.order_by(Comment.created_at.desc()).all()
        return render_template('post.html', post=post)
    except Exception as e:
        current_app.logger.error(f'Error viewing post {post_id}: {str(e)}', 
                               extra={'ip': request.remote_addr})
        return render_template('error.html', 
                             error_code=500, 
                             error_message='服务器内部错误'), 500

@main.route('/tag/<tag>')
def tag(tag):
    tag_obj = Tag.query.filter_by(name=tag).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = tag_obj.posts.paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    for post in posts.items:
        post.preview = md_to_html(post.content[:200] + '...' if len(post.content) > 200 else post.content)
    
    # 侧栏数据
    total_posts = Post.query.count()
    total_tags = Tag.query.count()
    total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
    
    # 最近文章
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    # 标签云数据
    tags = Tag.query.all()
    tag_counts = {tag.name: tag.posts.count() for tag in tags}
    max_count = max(tag_counts.values()) if tag_counts else 1
    
    return render_template('index.html', 
                         posts=posts,
                         current_tag=tag,
                         total_posts=total_posts,
                         total_tags=total_tags,
                         total_views=total_views,
                         recent_posts=recent_posts,
                         tags=tag_counts,
                         max_count=max_count)

@main.route('/tags')
def tags():
    tags = Tag.query.all()
    tag_counts = {tag.name: tag.posts.count() for tag in tags}
    
    # 侧栏数据
    total_posts = Post.query.count()
    total_tags = Tag.query.count()
    total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template('tags.html', 
                         tags=tag_counts,
                         total_posts=total_posts,
                         total_tags=total_tags,
                         total_views=total_views,
                         recent_posts=recent_posts)

@main.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    try:
        current_app.logger.info(f'Like request for post {post_id}')
        data = request.get_json()
        current_app.logger.debug(f'Request data: {data}')
        
        # 检查请求体
        if not data:
            return jsonify({'error': '无效的请求'}), 400

        # 检查是否已经点赞
        liked_posts = session.get('liked_posts', [])
        if not isinstance(liked_posts, list):
            liked_posts = []
            
        if post_id in liked_posts:
            return jsonify({'error': '已经点赞过了'}), 400
        
        post = Post.query.get_or_404(post_id)
        post.likes += 1
        
        # 记录点赞状态
        liked_posts.append(post_id)
        session['liked_posts'] = liked_posts
        session.modified = True
        
        db.session.commit()
        current_app.logger.info(f'Successfully liked post {post_id}')
        return jsonify({'likes': post.likes})
    except Exception as e:
        current_app.logger.error(f'Error liking post {post_id}: {str(e)}')
        return jsonify({'error': str(e)}), 500

@main.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    try:
        # 检查评论频率
        last_comment_time = session.get('last_comment_time')
        current_time = datetime.utcnow()
        
        if last_comment_time:
            try:
                last_time = datetime.fromisoformat(last_comment_time)
                time_diff = current_time - last_time
                if time_diff.total_seconds() < 60:  # 60秒内不能重复评论
                    return jsonify({
                        'success': False,
                        'error': '评论太频繁，请稍后再试'
                    }), 429
            except ValueError:
                # 如果时间格式无效，重置时间
                session.pop('last_comment_time', None)
        
        content = request.form.get('content', '').strip()
        author_name = request.form.get('author_name', '').strip()
        
        # 输入验证
        if not content:
            return jsonify({
                'success': False,
                'error': '评论内容不能为空'
            }), 400
            
        if len(content) > 1000:  # 添加长度限制
            return jsonify({
                'success': False,
                'error': '评论内容过长'
            }), 400
            
        if author_name and len(author_name) > 50:  # 添加昵称长度限制
            return jsonify({
                'success': False,
                'error': '昵称过长'
            }), 400
            
        if not author_name:
            author_name = '匿名用户'
            
        comment = Comment(
            content=content,
            author_name=author_name,
            post_id=post_id,
            ip_address=request.remote_addr  # 记录评论者IP
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # 更新评论时间
        session['last_comment_time'] = current_time.isoformat()
        session.modified = True
        
        # 返回新评论的HTML
        return jsonify({
            'success': True,
            'comment': {
                'author_name': comment.author_name,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error adding comment to post {post_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': '评论提交失败，请重试'
        }), 500

@main.route('/knowledge-graph')
def knowledge_graph():
    return render_template('knowledge_graph.html')

@main.route('/portfolio')
def portfolio():
    projects = Portfolio.query.order_by(Portfolio.order).all()
    
    # 侧栏数据
    total_posts = Post.query.count()
    total_tags = Tag.query.count()
    total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    tags = Tag.query.all()
    tag_counts = {tag.name: tag.posts.count() for tag in tags}
    max_count = max(tag_counts.values()) if tag_counts else 1
    
    return render_template('portfolio.html', 
                         projects=projects,
                         total_posts=total_posts,
                         total_tags=total_tags,
                         total_views=total_views,
                         recent_posts=recent_posts,
                         tags=tag_counts,
                         max_count=max_count)

@main.route('/about')
def about():
    about_content = '''
# 关于我

你好！我是一名热爱技术的开发者。

## 技术栈

- **后端**: Python, Flask, Django, Node.js
- **前端**: HTML, CSS, JavaScript, Vue.js
- **数据库**: MySQL, PostgreSQL, MongoDB
- **工具**: Git, Docker, Linux

## 项目经历

1. **鸭蛋橙博客系统**
   - 基于 Flask 的个人博客系统
   - 支持 Markdown 写作
   - 实现标签系统和搜索功能

2. **其他开源贡献**
   - 参与多个开源项目
   - 编写技术文档和教程

## 兴趣爱好

- 技术写作
- 开源项目
- 读书
- 摄影

## 联系我

如果你对我的项目感兴趣，或者想要交流技术，欢迎联系我！
    '''
    
    # 侧栏数据
    total_posts = Post.query.count()
    total_tags = Tag.query.count()
    total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    tags = Tag.query.all()
    tag_counts = {tag.name: tag.posts.count() for tag in tags}
    max_count = max(tag_counts.values()) if tag_counts else 1
    
    return render_template('about.html', 
                         about_content=md_to_html(about_content),
                         total_posts=total_posts,
                         total_tags=total_tags,
                         total_views=total_views,
                         recent_posts=recent_posts,
                         tags=tag_counts,
                         max_count=max_count)

@main.route('/search')
def search():
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        if query:
            posts = Post.query.filter(
                db.or_(
                    Post.title.ilike(f'%{query}%'),
                    Post.content.ilike(f'%{query}%')
                )
            ).paginate(
                page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
            for post in posts.items:
                post.preview = md_to_html(post.content[:200] + '...' if len(post.content) > 200 else post.content)
        else:
            posts = Post.query.paginate(page=1, per_page=current_app.config['POSTS_PER_PAGE'], total=0)
        
        # 侧栏数据
        total_posts = Post.query.count()
        total_tags = Tag.query.count()
        total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
        
        # 最近文章
        recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
        
        # 标签云数据
        tags = Tag.query.all()
        tag_counts = {tag.name: tag.posts.count() for tag in tags}
        max_count = max(tag_counts.values()) if tag_counts else 1
        
        return render_template('search.html', 
                            posts=posts,
                            query=query,
                            total_posts=total_posts,
                            total_tags=total_tags,
                            total_views=total_views,
                            recent_posts=recent_posts,
                            tags=tag_counts,
                            max_count=max_count)
    except Exception as e:
        current_app.logger.error(f'Search error: {str(e)}')
        return render_template('error.html', error_code=500, error_message='搜索功能暂时不可用'), 500

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message='页面未找到'), 404

@main.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message='服务器内部错误'), 500

@main.route('/sitemap.xml')
def sitemap():
    pages = []
    
    # 添加静态页面
    pages.append({
        'loc': url_for('main.index', _external=True),
        'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
        'changefreq': 'daily',
        'priority': '1.0'
    })
    
    # 添加文章页面
    posts = Post.query.all()
    for post in posts:
        pages.append({
            'loc': url_for('main.post', post_id=post.id, _external=True),
            'lastmod': post.updated_at.strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        })
    
    # 添加标签页面
    tags = Tag.query.all()
    for tag in tags:
        pages.append({
            'loc': url_for('main.tag', tag=tag.name, _external=True),
            'changefreq': 'weekly',
            'priority': '0.6'
        })
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response 

@main.route('/api/knowledge-graph')
def get_knowledge_graph_data():
    # 获取所有文章和标签
    posts = Post.query.all()
    tags = Tag.query.all()
    
    nodes = []
    links = []
    node_ids = set()
    connected_tags = set()  # 用于跟踪有连接的标签

    # 添加所有标签作为节点
    for tag in tags:
        post_count = Post.query.filter(Post.tags.contains(tag)).count()
        if post_count > 0:  # 只添加有文章的标签
            nodes.append({
                "id": tag.name,
                "label": tag.name,
                "group": 1,
                "type": "tag",
                "size": post_count
            })
            node_ids.add(tag.name)
            connected_tags.add(tag.name)  # 记录这个标签

    # 添加所有文章作为节点
    for post in posts:
        if len(post.tags) > 0:
            nodes.append({
                "id": f"post_{post.id}",
                "label": post.title,
                "group": 2,
                "type": "post",
                "size": 10,
                "post_id": post.id
            })
            node_ids.add(f"post_{post.id}")

            # 添加文章和标签之间的连接
            for tag in post.tags:
                links.append({
                    "source": f"post_{post.id}",
                    "target": tag.name,
                    "value": 1
                })
                connected_tags.add(tag.name)  # 记录这个标签被连接

    # 添加标签之间的关联（如果两个标签经常一起出现在同一篇文章中）
    tag_connections = defaultdict(int)
    for post in posts:
        post_tags = [tag for tag in post.tags if tag.name in connected_tags]  # 只使用有连接的标签
        for i in range(len(post_tags)):
            for j in range(i + 1, len(post_tags)):
                pair = tuple(sorted([post_tags[i].name, post_tags[j].name]))
                tag_connections[pair] += 1

    # 添加强关联的标签之间的连接
    for (tag1, tag2), weight in tag_connections.items():
        if weight > 1 and tag1 in connected_tags and tag2 in connected_tags:  # 确保两个标签都是有连接的
            links.append({
                "source": tag1,
                "target": tag2,
                "value": weight
            })

    # 过滤掉没有任何连接的节点
    connected_nodes = set()
    for link in links:
        connected_nodes.add(link['source'])
        connected_nodes.add(link['target'])
    
    nodes = [node for node in nodes if node['id'] in connected_nodes]

    return jsonify({"nodes": nodes, "links": links}) 

@main.app_errorhandler(Exception)
def handle_error(error):
    current_app.logger.error(f'Unhandled error: {str(error)}')
    return render_template('error.html', 
                         error_code=500, 
                         error_message='服务器内部错误'), 500 
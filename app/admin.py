from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, current_app
from functools import wraps
from app.models import Post, Tag, Comment
from app import db
from datetime import datetime
from flask_wtf.csrf import CSRFProtect, CSRFError

admin = Blueprint('admin', __name__, url_prefix='/admin')
csrf = CSRFProtect()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('请先登录')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码')
            current_app.logger.warning('Login attempt with missing credentials')
            return render_template('admin/login.html')
            
        if username == current_app.config['ADMIN_USERNAME'] and \
           password == current_app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            session.permanent = True
            current_app.logger.info(f'Successful login from IP: {request.remote_addr}')
            return redirect(url_for('admin.index'))
        else:
            flash('用户名或密码错误')
            current_app.logger.warning(
                f'Failed login attempt - Username: {username}, IP: {request.remote_addr}'
            )
            return render_template('admin/login.html')
            
    return render_template('admin/login.html')

@admin.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin.route('/')
@login_required
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/index.html', posts=posts)

@admin.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', '').split(',')
        
        post = Post(
            title=title,
            content=content,
            created_at=datetime.utcnow()
        )
        
        # 处理标签
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                post.add_tag(tag_name)
        
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('admin.index'))
    
    return render_template('admin/edit_post.html')

@admin.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        tags = request.form.get('tags', '').split(',')
        
        # 清除现有标签
        post.tags = []
        
        # 添加新标签
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                post.add_tag(tag_name)
        
        db.session.commit()
        return redirect(url_for('admin.index'))
    
    return render_template('admin/edit_post.html', post=post)

@admin.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin.index'))

@admin.route('/comments')
@login_required
def comments():
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/comments.html', comments=comments)

@admin.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@admin.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        comment.is_approved = True
        comment.approved_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@admin.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        content = request.json.get('content')
        if content:
            comment.content = content.strip()
            comment.edited_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': '内容不能为空'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@admin.before_request
def before_request():
    if not session.get('admin_logged_in') and \
       request.endpoint != 'admin.login':
        return redirect(url_for('admin.login')) 

@admin.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message='页面未找到'), 404

@admin.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message='服务器内部错误'), 500

@admin.errorhandler(CSRFError)
def handle_csrf_error(e):
    current_app.logger.error(f'CSRF Error: {str(e)}')
    current_app.logger.error(f'Request Headers: {dict(request.headers)}')
    current_app.logger.error(f'Request Form: {request.form}')
    return render_template('error.html',
                         error_code=400,
                         error_message='CSRF验证失败，请刷新页面重试'), 400 
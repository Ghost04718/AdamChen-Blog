from flask import Flask, request, has_request_context, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask import render_template

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

# 添加自定义日志过滤器
class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.ip = request.remote_addr
            record.url = request.url
            record.method = request.method
        else:
            record.ip = '-'
            record.url = '-'
            record.method = '-'
        return super().format(record)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # 注册蓝图
    from app.routes import main
    from app.admin import admin
    app.register_blueprint(main)
    app.register_blueprint(admin)
    
    # 配置日志
    if not app.debug and not app.testing:
        # 确保logs目录存在
        if not os.path.exists('logs'):
            os.makedirs('logs', mode=0o755)
            
        # 配置文件日志
        file_handler = RotatingFileHandler('logs/blog.log',
                                         maxBytes=1024*1024,
                                         backupCount=20)
        formatter = RequestFormatter(
            '%(asctime)s %(levelname)s: [%(ip)s %(method)s %(url)s] '
            '%(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Blog startup')
        
        # 生产环境特定配置
        if app.config['ENV'] == 'production':
            # 应用安全头部
            @app.after_request
            def add_security_headers(response):
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
                response.headers['X-Frame-Options'] = 'SAMEORIGIN'
                response.headers['X-Content-Type-Options'] = 'nosniff'
                response.headers['X-XSS-Protection'] = '1; mode=block'
                response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
                return response
    
    # CSRF错误处理
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        app.logger.warning(
            f'CSRF Error: {request.url} - IP: {request.remote_addr} - '
            f'Method: {request.method} - Referrer: {request.referrer}'
        )
        if request.is_xhr:
            return jsonify({
                'error': 'CSRF验证失败，请刷新页面重试',
                'code': 400
            }), 400
        return render_template('error.html', 
                             error_code=400, 
                             error_message='CSRF验证失败，请刷新页面重试'), 400
    
    # 其他错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {request.url}')
        return render_template('error.html', 
                             error_code=404, 
                             error_message='页面未找到'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {str(error)}')
        return render_template('error.html', 
                             error_code=500, 
                             error_message='服务器内部错误'), 500
    
    return app
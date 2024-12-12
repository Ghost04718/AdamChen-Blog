import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# 尝试加载.env文件，如果不存在则加载.flaskenv
if os.path.exists(os.path.join(basedir, '.env')):
    load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'generate-a-long-random-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///blog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10
    
    # 安全配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'change-this-password'
    
    # Cookie和会话安全设置
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # 生产环境强制HTTPS
    SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # 防止CSRF攻击
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN')  # 设置cookie域名
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    SERVER_NAME = os.environ.get('SERVER_NAME')  # 设置服务器域名
    
    # CSRF保护设置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF令牌有效期
    WTF_CSRF_SSL_STRICT = False  # 允许HTTP和HTTPS混用
    WTF_CSRF_CHECK_DEFAULT = True
    
    # Google Analytics and Search Console
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    GOOGLE_SITE_VERIFICATION = os.environ.get('GOOGLE_SITE_VERIFICATION')
    
    # 生产环境特定配置
    @staticmethod
    def init_app(app):
        if os.environ.get('FLASK_ENV') == 'production':
            # 启用安全头部
            app.config['SECURE_HEADERS'] = {
                'STRICT_TRANSPORT_SECURITY': True,
                'X_FRAME_OPTIONS': 'SAMEORIGIN',
                'X_CONTENT_TYPE_OPTIONS': 'nosniff',
                'X_XSS_PROTECTION': '1; mode=block',
                'REFERRER_POLICY': 'strict-origin-when-cross-origin'
            }
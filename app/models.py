from datetime import datetime
from app import db
from sqlalchemy import event

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Tag {self.name}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    daily_views = db.Column(db.Integer, default=0)  # 日访问量
    weekly_views = db.Column(db.Integer, default=0)  # 周访问量
    monthly_views = db.Column(db.Integer, default=0)  # 月访问量
    last_view_date = db.Column(db.Date)  # 最后访问日期
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def search(query):
        return Post.query.filter(
            db.or_(
                Post.title.ilike(f'%{query}%'),
                Post.content.ilike(f'%{query}%')
            )
        ).order_by(Post.created_at.desc()).all()

    def add_tag(self, tag_name):
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        if tag not in self.tags:
            self.tags.append(tag)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_name = db.Column(db.String(100))  # 添加评论者名称
    is_approved = db.Column(db.Boolean, default=False)  # 评论审核状态
    approved_at = db.Column(db.DateTime)  # 审核时间
    edited_at = db.Column(db.DateTime)    # 编辑时间
    ip_address = db.Column(db.String(45)) # 评论者IP

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    project_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    tags = db.Column(db.String(200))  # 逗号分隔的标签
    order = db.Column(db.Integer, default=0)  # 用于排序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
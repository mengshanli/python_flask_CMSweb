from exts import db
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

#%%
class Users(db.Model):
    __tablename__='jq_user'
    
    '''
    uid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(60), nullable=False)
    email=db.Column(db.String(60), nullable=False, unique=True)
    #password=db.Column(db.String(300), nullable=False)

    _password=db.Column(db.String(500), nullable=False)
    
    '''
    #p.285
    uid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(50), nullable=False,unique=True)
    email=db.Column(db.String(50), nullable=False, unique=True)
    _password=db.Column(db.String(100), nullable=False)
    is_super=db.Column(db.SmallInteger)
    role_id=db.Column(db.Integer, db.ForeignKey('jq_role.id'))
    reg_time=db.Column(db.DateTime, default=datetime.now)
    articles=db.relationship("Articles", lazy="dynamic")    
    
    
    
    
    def __init__(self, username, password, email):
        self.username=username
        self.password=password
        self.email=email
        
    @property
    def password(self):
        print('property')
        print(self._password)
        return self._password
    
    @password.setter 
    def password(self, raw_password):
        self._password=generate_password_hash(raw_password)
        print('set')
        print(self._password)
        
    def check_password(self, raw_password):
        result=check_password_hash(self.password, raw_password)
        print(self.password)
        print(raw_password)
        return result 

#%%
  
class Articles_Cat(db.Model):
    __tablename__='jq_article_category'
    cat_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id=db.Column(db.Integer, nullable=False)
    cat_name=db.Column(db.String(20), nullable=False)
    keywords=db.Column(db.String(20), nullable=False)
    description=db.Column(db.Text, nullable=True)
    cat_sort=db.Column(db.Integer, nullable=True)
    status=db.Column(db.Integer, nullable=False)
    dir=db.Column(db.String(80), nullable=False)
       
    articles = db.relationship("Articles", lazy="dynamic")#??????????????????????????????
    
    
    
#?????????????????????????????????
article_tag = db.Table('article_tag',
      db.Column('jq_article.aid',db.Integer,db.ForeignKey('jq_article.aid'),primary_key=True),
      db.Column('jq_tag.tid',db.Integer,db.ForeignKey('jq_tag.tid'),primary_key=True))
    


class Articles(db.Model):
    __tablename__='jq_article'
    aid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_id=db.Column(db.Integer, db.ForeignKey("jq_article_category.cat_id"))
    title=db.Column(db.String(255), nullable=False)
    shorttitle=db.Column(db.String(255), nullable=True)
    source=db.Column(db.String(64), nullable=False)
    keywords=db.Column(db.String(64), nullable=False)
    description=db.Column(db.String(512), nullable=False)
    
    body=db.Column(db.Text, nullable=False)
    clicks=db.Column(db.Integer, default=0)
    picture=db.Column(db.String(255))
    author_id=db.Column(db.Integer, db.ForeignKey('jq_user.uid'))
    
    allowcomments=db.Column(db.Integer, default=0)
    status=db.Column(db.Integer, default=0)
    create_time=db.Column(db.DateTime, default=datetime.now)
    
    is_delete=db.Column(db.Boolean, default=0)
    tags=db.relationship('Articles_Tag', secondary=article_tag,
                         backref=db.backref('articles'))
   

#??????????????????
class Articles_Tag(db.Model):
     __tablename__ = 'jq_tag'
     tid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ??????ID
     aid = db.Column(db.Integer)  # ??????,??????ID
     cat_id=db.Column(db.SmallInteger)#??????????????????????????????tag
     tag = db.Column(db.String(40), nullable=False)  # ????????????,nullable=false???????????????????????????????????????

#%%

#??????
class Comment(db.Model):
    __tablename__='jq_comment'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    aid=db.Column(db.Integer)#???????????????ID
    title=db.Column(db.String(255))#?????????????????????
    user_id=db.Column(db.Integer)#??????ID
    user_name=db.Column(db.String(200))#?????????
    comment=db.Column(db.Text)#????????????
    status = db.Column(db.Integer, default=0)# ?????????????????? ?????????0?????????????????????1??????????????????-1?????????????????????
    parent_id=db.Column(db.Integer)#????????????ID
    comment_ip=db.Column(db.String(255))#????????????IP??????
    add_time=db.Column(db.DateTime,default=datetime.now)#??????????????????

#%%

    

class Admin_Log(db.Model):
    __tablename__ = "jq_adminlog"
    id=db.Column(db.Integer, primary_key=True)
    admin_id=db.Column(db.Integer, db.ForeignKey('jq_user.uid'))
    operate=db.Column(db.String(300))
    ip=db.Column(db.String(100))
    add_time=db.Column(db.DateTime, index=True, default=datetime.now)
    
#%%
    
class Auth(db.Model):
    __tablename__="jq_auth"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), unique=True)
    url=db.Column(db.String(255), unique=True)
    add_time=db.Column(db.DateTime, index=True, default=datetime.utcnow)
    parent_id=db.Column(db.Integer)
    status=db.Column(db.Integer)
 
    
#%%
    
class Role(db.Model):
    __tablename__ = "jq_role"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), unique=True)
    auths=db.Column(db.String(600))
    add_time=db.Column(db.DateTime, index=True, default=datetime.utcnow)
    description=db.Column(db.String(300))
    admins=db.relationship("Users", backref='jq_role')
    

    
        
        
        
        
        
        
    
    
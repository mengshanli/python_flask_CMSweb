#encoding:utf-8

from exts import db
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash


class Members(db.Model):
    __tablename__='jq_member'
    uid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(50), nullable=False, unique=True)
    email=db.Column(db.String(50), nullable=False, unique=True)

    _password=db.Column(db.String(255), nullable=False)
    
    vatar=db.Column(db.String(80), nullable=True)
    nickname=db.Column(db.String(50), nullable=True)
    sex=db.Column(db.String(2), default=0)
    telephone=db.Column(db.String(11))
    status=db.Column(db.Integer)
   
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
        #print('compare')
        #print(self.password)
        #print(raw_password)
        result=check_password_hash(self.password, raw_password)
        print('result')
        print(result)
        return result 
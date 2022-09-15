#encoding:utf-8

from wtforms import Form
from wtforms import StringField, BooleanField
from wtforms.validators import InputRequired, Length, Email

class LoginForm(Form):
    username=StringField(
        label='用戶名',
        validators=[
            InputRequired('用戶名必填'),
            Length(4,20,'用戶名長度為4到20')
            ]
        )
    
    password=StringField(
        label='密碼',
        validators=[
            InputRequired('密碼必填'),
            Length(6,20,'密碼長度6到20')
            ]
        )
    
    
class Article_cat(Form):
    parent_id=StringField(validators=[Length(1,20,message="父欄目長度為1-20位")])
    cat_name=StringField(validators=[Length(1,100,message="欄目名字長度為1-100位")])
    dir=StringField(validators=[Length(0,100,message="別名長度為0-100位")])
    keywords=StringField(validators=[Length(1,100,message="關鍵字長度為1-100位")])
    description=StringField(validators=[Length(1,200,message="欄目描述長度為1-200位")])
    cat_sort=StringField(validators=[Length(1,100,message="欄目排序長度為1-100位")])


class Article(Form):
    cat_id=StringField(validators=[Length(1,20,message='欄目為1-20位')])
    title=StringField(validators=[Length(2,120,message='文章標題長度為2-120位')])
    shorttitle=StringField(validators=[Length(2,20,message='短標題長度為2-20位')])
    source=StringField(validators=[Length(1,50,message='文章來源長度為1-50位')])
    keywords=StringField(validators=[Length(1,30,message='關鍵字長度為1-20位')])
    description=StringField(validators=[Length(1,200,message='摘要長度為1-20位')])
    body=StringField(validators=[Length(0,20000000,message='文章內容長度為1-20位')])
    picture=StringField(validators=[Length(1,200,message='縮略圖長度為1-200位')])
    author_id=StringField(validators=[Length(1,30,message='作者名稱長度為1-30位')])
    allowcomments=StringField(validators=[Length(1,2,message='允許評論長度為1-2位')])
    status=StringField(validators=[Length(1,2,message='發佈狀態長度為1-2位')])


#%%

class Checek_Auth(Form):
    url = StringField(validators=[Length(1, 100, message='父栏目长度为1-100位')])
    name = StringField(validators=[Length(1, 100, message='栏目名字长度为1-100位')])
    parent_id = StringField(validators=[Length(1, 30, message='上级栏目长度为1-100位')])
    status = StringField(validators=[Length(1, 6, message='上级栏目长度为1-6位')])

#%%

#角色表单验证
class Checek_Role(Form):
    auths = StringField(validators=[Length(1, 100, message='父栏目长度为1-100位')])
    name = StringField(validators=[Length(1, 100, message='栏目名字长度为1-100位')])
    description = StringField(validators=[Length(1, 300, message='上级栏目长度为1-100位')])
    
    
    
    
    
    
    
    
    
    
    

from wtforms import Form
from wtforms import StringField, BooleanField, SubmitField 
from wtforms.validators import InputRequired, Length, Email, DataRequired 


    
class RegisterForm(Form):
    username= StringField(
        label='用户名',
        validators=[
            InputRequired('用戶名為必填項'),
            Length(6, 15, '用戶名長度為6到15')
        ]
    )
    password1 = StringField(
        label='密码',
        validators=[
            InputRequired('密碼為必填項'),
            Length(6, 30, '密碼長度為6到30')
        ]
    )
    password2 = StringField(
        label='密码',
        validators=[
            InputRequired('密碼為必填項'),
            Length(6, 30, '密碼長度為6到30')
        ]
    )
    email = StringField(validators=[Length(0, 100, message='信箱長度為0到100')])
    

class LoginForm(Form):
    username=StringField(
        label='用戶名',
        validators=[
            InputRequired('用戶名為必填項'),
            Length(6,15,'用戶名長度為6-15')
            ]
        )
    password=StringField(
        label='密碼',
        validators=[
            InputRequired('密碼為必填項'),
            Length(6,15,'密碼長度為6-15')
            ]
        )
    
    
  
    
#评论表单验证
class CommentForm(Form):
    comment_content = StringField("評論內容:", validators=[DataRequired("請輸入評論"),Length(1, 600)], render_kw={"placeholder": "請輸入評論內容"})
    captcha = StringField("驗證碼:", validators=[DataRequired("請輸入驗證碼")],render_kw={"placeholder": "請輸入驗證碼"})
    article_id = StringField("文章ID：", validators=[DataRequired("請輸入文章ID")],render_kw={"placeholder": "請輸入文章ID"})
    article_title= StringField("文章標題:", validators=[DataRequired("請輸入文章標題")],render_kw={"placeholder": "請輸入文章標題"})
    submit = SubmitField('評 論')
#encoding:utf-8
from flask import Blueprint
bp=Blueprint("front", __name__)

@bp.route("/")
def index1(): #原本是index
    return "這是前台首頁!"


from flask import render_template, request, session, redirect, url_for, flash
from .models import Members
from exts import db


from .forms import LoginForm, RegisterForm
from datetime import timedelta, datetime

from config import MEMBER_USER_ID

from .recursion import build_cat_tree, build_cat_table


#p.324
import sys 
sys.path.append('../')
from ..admin.models import Articles, Articles_Cat, Users,Comment

from .forms import CommentForm

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('front/register.html')
    if request.method == 'POST':
        form=RegisterForm(request.form)

        username=form.username.data
        password1=form.password1.data
        password2=form.password2.data
        email=form.email.data

        
        if password1 != password2:
            flash('兩次輸入的密碼不一樣', 'error')
        else:
            user=Members(username=username,
                         password=password1,
                         email=email)
            db.session.add(user)
            db.session.commit()
            flash('註冊成功，請登錄', 'ok')
        return redirect(url_for('front.register'))
    





@bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        url=request.args.get('url')
        if url == '/log_out':
            url='/'
        if url == None:
            session['url']=None
        else:
            session['url']=url
        return render_template('front/login.html')
    else:
        form=LoginForm(request.form)
        if form.validate():
            username=form.username.data
            password=form.password.data 
            users=Members.query.filter_by(username=username).first()
           
            if users:
                if username == users.username and users.check_password(password):
                    session[MEMBER_USER_ID]=users.username
                    session.permanent=True
                    bp.permanent_session_lifetime=timedelta(days=7)
                else:
                    flash('用戶帳號或密碼錯誤', 'error')
                    return redirect(url_for('front.login'))
            else:
                flash('用戶帳號或密碼錯誤', 'error')
                return redirect(url_for('front.login'))
        else:
            errors=form.errors
            flash(errors, 'error')
            return redirect(url_for('front.login'))
        
        username=session.get(MEMBER_USER_ID)
        session['username']=username
        if session['url'] == None:
            return render_template('front/index.html', username=username)
        else:
            return redirect(session['url'])
                
                

@bp.route('/log_out')
def log_out():
    session.pop(MEMBER_USER_ID, None)
    session.pop('username', None)
    return redirect(url_for('front.index'))




@bp.route('/', methods=['GET', 'POST'])
def index(): 
    list=[]
    data={}
    if request.method == 'GET':
        nav=Articles_Cat.query.all()
        for cat in nav:
            data=dict(cat_id=cat.id,
                      parent_id=cat.parent_id,
                      cat_name=cat.cat_name)
            list.append(data)
        
        cat=build_cat_tree(list,0,0)
        zz=build_cat_table(cat, parent_title='頂級菜單')
        news1=Articles.query.all()
        return render_template('front/index.html', cat=zz, news1=news1)




@bp.route('/article_details/<int:id>', methods=['GET','POST'])
def article_details(id):
    if request.method == 'GET':
        news1=Articles.query.filter(Articles.aid == id).first_or_404()
        author1=Users.query.filter(Users.uid == news1.author_id).first()
        if author1:
            author=author1.username
        else:
            author='無名'
        db.session.query(Articles).filter_by(aid=id).update({Articles.clicks: Articles.clicks +1})
        db.session.commit()
        
        news2=Articles.query.filter(Articles.aid < id).order_by(Articles.aid.desc()).first()
        news3=Articles.query.filter(Articles.aid > id).order_by(Articles.aid.desc()).first()
        news4=Articles.query.filter(Articles.is_delete == 0).order_by(Articles.clicks.desc()).limit(5)
        
        list=[]
        data={}
        nav=Articles_Cat.query.all()
        for cat in nav:
            data=dict(cat_id=cat.cat_id,
                      parent_id=cat.parent_id,
                      cat_name=cat.cat_name)
            list.append(data)
        
        cat=build_cat_tree(list,0,0)
        zz=build_cat_table(cat, parent_title='頂級菜單')
        return render_template('front/article_details.html', 
                               cat=zz, news1=news1, news2=news2, news3=news3,
                               news4=news4, author=author)
    
    else:
        if request.method == 'POST':
            form=CommentForm(request.form)
            data=form.data
            id=data['article_id']
            if session.get('username') == None:
                url =url_for('front.login')+'?url=article_details/'+id
                return redirect(url)
            if form.validate():
                comment_content=data['comment_content']
                captcha=data['captcha']
                id=data['article_id']
                title=data['article_title']
                if session.get('image').lower() != captcha.lower():
                    flash('驗證碼錯誤', 'error')
                else:
                    username=session.get('username')
                    user=Members.query.filter(Members.username == username).first_or_404()
                    uid=user.uid
                    
                    post=Comment(
                        title=title,
                        aid=id,
                        comment=comment_content,
                        status=0,
                        parent_id=1,
                        add_time=datetime.datetime.now(),
                        user_name=session.get('username'),
                        user_id=uid,
                        comment_ip=request.remote_addr
                        )
                    db.session.add(post)
                    db.session.commit()
                    flash('評論添加成功', 'ok')
                    return redirect(url_for('front.article_details'), id=id)
            else:
                errors=form.errors
                flash(errors, 'error')
                return redirect(url_for('front.article_details', id=id))






@bp.app_errorhandler(404)
def error_404(error):
    return render_template('front/404.html'),404

@bp.app_errorhandler(500)
def error_500(error):
    return render_template('front/404.html'),500



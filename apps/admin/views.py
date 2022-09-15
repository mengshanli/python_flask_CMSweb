#encoding:utf-8


from .models import Articles_Cat
from .forms import Article_cat
from xpinyin import Pinyin

from .models import Articles
from .forms import Article

from sqlalchemy import func#统计查询使用


from .models import Comment
from .recursion import creat_commont_tree, creat_table

from .models import Admin_Log

from .models import Auth
from .recursion import build_auth_tree, build_auth_table
from .forms import Checek_Auth

from .models import Role
from .forms import Checek_Role
from .recursion import creat_auth_table

from .decorators import admin_auth
#from flask import json
#from utils.captcha import create_validate_code

#from sqlalchemy import and_#多个添加查询
#import os
#import re
#import memcache



#%%
#ch9
from flask import Blueprint, render_template, request, session, redirect, url_for
from .models import Users
from .forms import LoginForm
from flask import make_response #驗證碼
from utils.captcha import create_validate_code #驗證碼
from io import BytesIO #驗證碼
from datetime import timedelta #記住我功能
from .decorators import login_required
#from flask import g
import config
from exts import db

bp=Blueprint("admin", __name__, url_prefix='/admin')

@bp.route("/login/", methods=['GET', 'POST'])
def login():
    print('login')
    error=None 
    if request.method == 'GET':
        return render_template('admin/login.html')
    else:

        form=LoginForm(request.form)
        if form.validate():
            captcha=request.form.get('captcha')
            if session.get('image').lower() != captcha.lower():
                return render_template('admin/login.html', message="wrong validation code")
            
            user=request.form.get('username') 
            pwd=request.form.get('password')
            users=Users.query.filter_by(username=user).first()
            
            
            #不確定是不是放這裡
            online=request.form.get('online')
            if online:
                session.permanent=True
                bp.permanent_session_lifetime=timedelta(days=14)
             
                
                
            if users:
                if user == users.username and users.check_password(pwd):
                    session[config.ADMIN_USER_ID]=users.uid
                    #session['user_id']=users.uid
                    
                    #p.274
                    user_id=session.get(config.ADMIN_USER_ID)
                    oplog=Admin_Log(
                        admin_id=user_id,
                        ip=request.remote_addr,
                        operate="用戶: "+users.username+"進行了登錄動作")
                    db.session.add(oplog)
                    db.session.commit()
                    

                    print('correct password')
                    return redirect(url_for('admin.index'))
                else:
                    print('wrong username or wrong password')
                    error="wrong username or wrong password"
                    return render_template('admin/login.html', message=error)
            else:
                print('not exist')
                return render_template('admin/login.html', message="user is not exist")
        else:
            return render_template('admin/login.html', message=form.errors)


#調用驗證碼
@bp.route('/code/')
def get_code():
    code_img, strs=create_validate_code()
    buf=BytesIO()
    code_img.save(buf, 'JPEG', quality=70)
    buf_str=buf.getvalue()
    response=make_response(buf_str)
    response.headers['Content-Type']='image/jpeg'
    session['image']=strs
    return response



#登錄限制裝飾器
@bp.route('/test/')
@login_required 
def test():
    print("test")
    return 'test index'


#先登入才能登出
@bp.route('/logout/')
@login_required
def logout():
    #del session[user_id]
    print('logout')
    del session[config.ADMIN_USER_ID]
    print(config.ADMIN_USER_ID in session)
    return redirect(url_for('admin.login'))

#%%
#ch10-1
from flask import jsonify

#管理員個人訊息頁
@bp.route('/profile/')
@login_required 
def profile():
    print('profile')
    print(config.ADMIN_USER_ID)

    if config.ADMIN_USER_ID in session:
        user_id=session.get(config.ADMIN_USER_ID)
        user=Users.query.get(user_id) 
    return render_template('admin/profile.html', user=user)


#管理員更改密碼-比對密碼
@bp.route('/checkpwd/')
@login_required 
def checkpwd():
    oldpwd=request.args.get('oldpwd','')
    if config.ADMIN_USER_ID in session:
        user_id=session.get(config.ADMIN_USER_ID)
        user=Users.query.filter_by(uid=user_id).first()
        print("checkpwd")
        if user.check_password(oldpwd):
            data={
                "name":user.email,
                "status":11
                }
        else:
            data={
                "name":None,
                "status":00
                }
        return jsonify(data)

#管理員更改密碼-更改密碼
@bp.route('/editpwd/', methods=['GET', 'POST'])
@login_required
def editpwd():
    if request.method == 'GET':
        return render_template('admin/edit_pwd.html')
    else:
        oldpwd=request.form.get('oldpwd')
        newpwd1=request.form.get('newpwd1')
        newpwd2=request.form.get('newpwd2')
        print(oldpwd)
        user_id=session.get(config.ADMIN_USER_ID)
        user=Users.query.filter_by(uid=user_id).first()
        user.password=newpwd1 
        db.session.commit()
        return render_template('admin/edit_pwd.html', message="密碼修改成功")

#%%
#ch10-2

def build_tree(data, p_id, level=0):
    tree=[]
    for row in data:
        if row['parent_id'] == p_id:
            row['level']=level
            child=build_tree(data, row['cat_id'], level+1) #把child(parent_id=1)包成一包在parent_id=0底下
            row['child']=[]
            if child:
                row['child'] += child 
            tree.append(row)
    return tree
            
def build_table(data, parent_title='頂級菜單'):
    html=''
    for row in data:
        splice='├'
        cat_id=row['cat_id']
        title=splice * row['level'] + row['cat_name']
        tr_td="""<option value={cat_id}>{title}</option>
                            """
        if row['child']:
            html += tr_td.format(class_name='top_menu', title=title,
                                 cat_id=cat_id)
            html += build_table(row['child'], row['cat_name'])
        else:
            html += tr_td.format(class_name='', title=title,
                                 cat_id=cat_id)
    return html




#生成分类列表
# for def article_cat_list()
def creat_cat_list(data, parent_title='顶级菜单'):
    html = ''
    for row in data:
        splice = '-- '
        cat_id=row['cat_id']
        cat_sort = row['cat_sort']
        title = splice * row['level'] + row['cat_name']
        description = row['description']
        dir = row['dir']
        
        #href="article.php?cat_id={cat_id}"=??
        #<tr style="display:none"> 
        tr_td = """<tr>
        <td align="left"> <a href="article.php?cat_id={cat_id}"></a>{title}</td>
        <td>{dir}</td>
        <td>{description}</td>
        <td align="center">{cat_sort}</td>
        <td align="center"><a href="../article_cat_edit/{cat_id}" >编辑</a>| 
        <a href="../article_cat_del/{cat_id}" onClick="rec();return false">删除</a> </td>
      </tr>
                                   """


        if row['child']:
            html += tr_td.format(class_name='', title=title,cat_id=cat_id, 
                                 description= description,dir=dir,cat_sort=cat_sort)
            html += creat_cat_list(row['child'], row['cat_name'])
        else:
            html += tr_td.format(class_name='-', title=title,cat_id=cat_id,
                                 description= description,dir=dir,cat_sort=cat_sort)
            # return html
    return html








@bp.route('/article_cat_add/', methods=['GET', 'POST'])
@login_required 
@admin_auth #p.310
def article_cat_add():
    if request.method == 'GET':
        categorys=Articles_Cat.query.all()
        list=[]
        data={}
        for cat in categorys:
            data=dict(cat_id=cat.cat_id, parent_id=cat.parent_id,
                      cat_name=cat.cat_name)
            list.append(data)
        data=build_tree(list,0,0)
        html=build_table(data, parent_title='頂級菜單')
        return render_template('admin/article_cat.html', message=html)
    else:
        form=Article_cat(request.form)
        p=Pinyin()
        dir=request.form.get('dir')
        if form.validate():
            parent_id=request.form.get('parent_id')
            cat_name=request.form.get('cat_name')
            dir=request.form.get('dir')
            check=request.form.get('check')
            print('check: '+check)
            if check:
                dir=request.form.get('cat_name')
                dir=p.get_pinyin(dir, '')
            else:
                if dir:
                    dir=request.form.get('dir')
                else:
                    dir=request.form.get('cat_name')
                    dir=p.get_pinyin(dir, '')
            keywords=request.form.get('keywords')
            description=request.form.get('description')
            cat_sort=request.form.get('cat_sort')
            status=request.form.get('status')
            
            insert=Articles_Cat(parent_id=parent_id,
                                cat_name=cat_name,
                                dir=dir,
                                keywords=keywords,
                                description=description,
                                cat_sort=cat_sort,
                                status=status)
            db.session.add(insert)
            db.session.commit()
            return redirect(url_for('admin.article_cat_list'))
        else:
            return '校驗沒通過'
        

@bp.route('/article_cat_list/', methods=['GET'])
@login_required 
@admin_auth #p.310
def article_cat_list():
    if request.method == 'GET':
        categorys=Articles_Cat.query.all()
        list=[]
        data={}
        for cat in categorys:
            data=dict(cat_id=cat.cat_id, 
                      parent_id=cat.parent_id,
                      cat_name=cat.cat_name,
                      description=cat.description,
                      dir=cat.dir,
                      cat_sort=cat.cat_sort)
            list.append(data)
        data=build_tree(list,0,0)
        html=creat_cat_list(data, parent_title='頂級菜單')
        return render_template('admin/article_cat_list.html', message=html)







@bp.route('/article_cat_edit/<id>/', methods=['GET'])
@login_required 
@admin_auth #p.310
def article_cat_edit(id):
    if request.method == 'GET':
        cat_list=Articles_Cat.query.filter_by(cat_id=id).first()
        categorys=Articles_Cat.query.all()
        list=[]
        data={}
        for cat in categorys:
            data=dict(cat_id=cat.cat_id, parent_id=cat.parent_id,
                      cat_name=cat.cat_name)
            list.append(data)
        data=build_tree(list,0,0)
        html=build_table(data, parent_title='頂級菜單')
        return render_template('admin/article_cat_edit.html', content=
                               cat_list, message=html)
        
        
@bp.route('/article_cat_save/', methods=['POST'])
@login_required 
@admin_auth #p.310
def article_cat_save():
    form=Article_cat(request.form)
    p=Pinyin() 
    if form.validate():
        parent_id=request.form.get('parent_id')
        cat_id=int(request.form.get('cat_id'))
        cat_name=request.form.get('cat_name')
        dir=request.form.get('dir')
        check=request.form.get('check')
        if check:
            dir=request.form.get('cat_name')
            dir=p.get_pinyin(dir, '')
        else:
            if dir:
                dir=request.form.get('dir')
            else:
                dir=request.form.get('cat_name')
                dir=p.get_pinyin(dir, '')
        keywords=request.form.get('keywords')
        description=request.form.get('description')
        cat_sort=request.form.get('cat_sort')
        status=request.form.get('status')
        
        Articles_Cat.query.filter(Articles_Cat.cat_id == cat_id).update({
            Articles_Cat.parent_id:parent_id,
            Articles_Cat.cat_name:cat_name,
            Articles_Cat.dir:dir,
            Articles_Cat.keywords:keywords,
            Articles_Cat.description:description,
            Articles_Cat.cat_sort:cat_sort,
            Articles_Cat.status:status
            })
        db.session.commit()
        return redirect(url_for('admin.article_cat_list'))


@bp.route('/article_cat_del/<id>', methods=['GET'])
@login_required 
def article_cat_del(id):
    cat1=Articles_Cat.query.filter(Articles_Cat.cat_id == id).first()
    db.session.delete(cat1)
    db.session.commit()
    return redirect(url_for('admin.article_cat_list'))
        
#%%

@bp.route('/article_add', methods=['GET', 'POST'])
@login_required 
@admin_auth #p.310
def article_add():
    if request.method == 'GET':
        categorys=Articles_Cat.query.all()
        list=[]
        data={}
        for cat in categorys:
            data=dict(cat_id=cat.cat_id, parent_id=cat.parent_id,
                      cat_name=cat.cat_name)
            list.append(data)
        data=build_tree(list,0,0)
        html=build_table(data, parent_title='頂級菜單')
        return render_template('admin/article_add.html', cat=html)
    else:
        form=Article(request.form)
        if form.validate():
            title=request.form['title']
            shorttitle=request.form['shorttitle']
            cat_id=request.form['cat_id']
            keywords=request.form['keywords']
            description=request.form['description']
            author_id=request.form['author_id']
            user_id=session.get(config.ADMIN_USER_ID)
            
            author_id=user_id
            
            source=request.form['source']
            allowcomments=request.form['allowcomments']
            status=request.form.get('status')
            picture=request.form['picture']
            body=request.form['editorValue']
            
            article1=Articles(title=title,
                              shorttitle=shorttitle,
                              cat_id=cat_id,
                              keywords=keywords,
                              description=description,
                              author_id=author_id,
                              source=source,
                              allowcomments=allowcomments,
                              status=status,
                              picture=picture,
                              body=body)
            db.session.add(article1)
            db.session.commit()
            rows=Articles.query.filter(Articles.status == 0).all()
            return render_template('admin/article_list.html', rows=rows)
        else:
            errors=form.errors
            return render_template('admin/article_add.html', errors=errors)
            
    


@bp.route('/article_list', methods=['GET', 'POST'])
def article_list():
    if request.method == 'GET':
        rows=db.session.query(Articles).filter(Articles.is_delete == 0).all()
        total=db.session.query(func.count(Articles.aid)).filter(Articles.is_delete == 0).scalar()
        return render_template('admin/article_list.html',rows=rows,
                               total=total)




#搜索处理
@bp.route('/search_list/',methods=['GET','POST'])
def search_list():
    PAGESIZE=2#分页大小，每页显示2条
    current_page=1#当前第几页，默认第一页
    count=0#总记录数
    total_page=0#一共有多少页
    if request.method=='GET':
        current_page = request.args.get("p", '')  # 传过来第几页数 current_page
        key=request.args.get("key",'')
        show_shouye_status = 0  # 显示首页状态

        if current_page == '':
            current_page = 1
        else:
            current_page = int(current_page)
            if current_page > 1:
                show_shouye_status = 1
        #获取总记录数
        # count = db.session.query(func.count(Articles.aid)).filter(Articles.status == 0).scalar()
        count = db.session.query(func.count(Articles.aid)).filter(Articles.status == 0).filter(Articles.title.like('%'+key+'%')).scalar()
        #获取分页数
        zone=int(count%PAGESIZE)
        if zone==0:
            total_page=int(count/PAGESIZE)
        else:
            total_page = int(count/PAGESIZE +1)
            # article=Articles.query.filter(Articles.status==0).all()
        arts=db.session.query(Articles).filter(Articles.status == 0).filter(Articles.title.like('%'+key+'%')).limit(PAGESIZE).offset((int(current_page) - 1) * PAGESIZE).all()
        datas = {
            'user_list': 'admin/search_list/',#http://127.0.0.1:5000/admin/search_list/?p=2
            'p': int(current_page),
            'total': total_page,
            'count': count,
            'show_shouye_status': show_shouye_status,
            'dic_list': arts

        }
        return render_template('admin/search_list.html',datas=datas,key=key)


@bp.route('/article_del', methods=['GET', 'POST'])
def article_del():
    if request.method == 'POST':
        id=request.values.get('aid')
        db.session.query(Articles).filter_by(aid=id).update({Articles.is_delete:1})
        db.session.commit()
        data={
            "msg":"保存成功",
            "success":1
            }
        return jsonify(data)


@bp.route('/article_all_del', methods=['GET', 'POST'])
def article_all_del():
    if request.method == 'POST':
        id=list(request.values.get('aid'))
       
        articles=db.session.query(Articles).filter(Articles.aid.in_(id)).all()
        for art in articles:
            art.is_delete=1
            db.session.commit()
        data={
            "msg":"保存成功",
            "success":1
            }
    return jsonify(data)



@bp.route('article_edit/<id>', methods=['GET'])
def article_edit(id):
    if request.method == 'GET':
        categorys=Articles_Cat.query.all()
        list=[]
        data={}
        for cat in categorys:
            data=dict(cat_id=cat.cat_id, parent_id=cat.parent_id,
                      cat_name=cat.cat_name)
            list.append(data)
        data=build_tree(list,0,0)
        html=build_table(data, parent_title='頂級菜單')
        article=Articles.query.filter(Articles.aid == id).first()
        
        user=Users.query.filter(Users.uid == article.author_id).first()
        print('user: ')
        print(user)
        if user:
            username=user.username
        else:
            username='admin' 
        return render_template('admin/article_edit.html', article=article,
                               cat=html, username=username)
    


@bp.route('article_edit_save', methods=['POST'])
def article_edit_save():
    errors=None
    if request.method == 'POST':
        form=Article(request.form)
        if form.validate():
            id=request.form['article_id']
            title=request.form['title']
            shorttitle=request.form['shorttitle']
            cat_id=request.form['cat_id']
            keywords=request.form['keywords']
            description=request.form['description']
            author_id=request.form['author_id_new']
                      
            source=request.form['source']
            allowcomments=request.form['allowcomments']
            status=request.form.get('status')
            picture=request.form['picture']
            
            #提交表單時，編輯器中編寫的內容預設名稱是editorValue
            body=request.form['editorValue'] 
            
            Articles.query.filter(Articles.aid == id).update(
                {Articles.title:title,
                 Articles.shorttitle:shorttitle,
                 Articles.cat_id:cat_id,
                 Articles.keywords:keywords,
                 Articles.description:description,
                 Articles.author_id:author_id,
                 Articles.source:source,
                 Articles.allowcomments:allowcomments,
                 Articles.status:status,
                 Articles.picture:picture,
                 Articles.body:body
                 })
            db.session.commit()
        else:
            if form.errors:
                errors=form.errors
            else:
                errors=None
            print(errors)
        data={
            "msg":"修改成功",
            "success":1,
            "errors":errors
            }
        return jsonify(data)


#%%


@bp.route('/comment_list/', methods=['GET'])
def comment_list():
    test_commont1=Comment(
        aid=2,
        title='測試1',
        user_id=1,
        user_name='admin',
        comment='評論1',
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr 
        )
    test_commont2=Comment(
        aid=2,
        title='測試1',
        user_id=2,
        user_name='admin',
        comment='評論1',
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr 
        )
    test_commont3=Comment(
        aid=2,
        title='測試1',
        user_id=1,
        user_name='admin',
        comment='評論2',
        status=0,
        parent_id=1,
        comment_ip=request.remote_addr 
        )
    test_commont4=Comment(
        aid=2,
        title='測試1',
        user_id=1,
        user_name='admin',
        comment='評論3',
        status=0,
        parent_id=1,
        comment_ip=request.remote_addr 
        )
    test_commont5=Comment(
        aid=2,
        title='測試4',
        user_id=1,
        user_name='admin',
        comment='評論4',
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr 
        )
    test_commont6=Comment(
        aid=2,
        title='測試6',
        user_id=1,
        user_name='admin',
        comment='評論6',
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr 
        )
    test_commont7=Comment(
        aid=2,
        title='測試7',
        user_id=1,
        user_name='admin',
        comment='評論7',
        status=0,
        parent_id=0,
        comment_ip=request.remote_addr 
        )
    
    #db.session.add(test_commont1)
    #db.session.add(test_commont2)
    #db.session.add(test_commont3)
    #db.session.add(test_commont4)
    #db.session.add(test_commont5)
    #db.session.add(test_commont6)
    #db.session.add(test_commont7)
    #db.session.commit()
    
    #return render_template('admin/admin_article_common_list.html')
    
    PAGESIZE=2
    current_page=1
    count=0
    total_page=0
    list=[]
    data={}
    list1=[]
    if request.method == 'GET':
        current_page=request.args.get('p','')
        show_shouye_status=0
        is_end_page=0
        if current_page == '':
            current_page=1
        else:
            current_page=int(current_page)
            if current_page > 1:
                show_shouye_status = 1
        
        #母評論數量
        count=db.session.query(func.count(Comment.id)).filter(Comment.parent_id == 0).scalar()

        zone=int(count % PAGESIZE)
        if zone == 0:
            total_page=int(count/PAGESIZE)
        else:
            total_page=int(count/PAGESIZE +1)
            
        if current_page == total_page:
            is_end_page=1
        else:
            is_end_page=0
        
        #一頁2則評論+其所有子評論
        commonts=Comment.query.filter(Comment.parent_id == 0).limit(PAGESIZE).offset((int(current_page) -1)*PAGESIZE).all()
        for row1 in commonts:
            list1.append(row1)
            commonts1=Comment.query.filter(Comment.parent_id == row1.id).all()
            for row2 in commonts1:
                list1.append(row2)
        
        for comment2 in list1:
            data=dict(id=comment2.id, aid=comment2.aid, 
                      title=comment2.title,
                      user_id=comment2.user_id,
                      user_name=comment2.user_name,
                      comment=comment2.comment,
                      parent_id=comment2.parent_id,
                      status=comment2.status,
                      add_time=comment2.add_time,
                      comment_ip=comment2.comment_ip)
            list.append(data)
        
        zz=creat_commont_tree(list,0,0)
        html=creat_table(zz, parent_title='頂級菜單')
        datas={
            'page_list':'admin/comment_list/',
            'p':int(current_page),
            'total':total_page,
            'count':count,
            'show_shouye_status':show_shouye_status,
            'is_end_page':is_end_page,
            'dic_list':html}
        
        return render_template('admin/admin_article_common_list.html',
                               datas=datas)


    
@bp.route('comment_stop/', methods=['POST'])
def comment_stop():
        id=int(request.values.get('aid'))
        db.session.query(Comment).filter_by(id=id).update({Comment.status:-1})
        db.session.commit()
        data={
            "msg":"修改成功",
            "success":1,
            "errors":"錯誤"
            }
        return jsonify(data)

    
@bp.route('comment_start/', methods=['POST'])
def comment_start():
        id=int(request.values.get('aid'))
        db.session.query(Comment).filter_by(id=id).update({Comment.status:0})
        db.session.commit()
        data={
            "msg":"修改成功",
            "success":1,
            "errors":"錯誤"
            }
        return jsonify(data)

# 刪除母評論時會把其子評論也全刪掉，每頁維持2則母評論
@bp.route('comment_del/', methods=['POST'])
def comment_del():
        id=int(request.values.get('aid'))
        comment1=db.session.query(Comment).filter_by(id=id).first()
        db.session.delete(comment1)
        db.session.commit()
        data={
            "msg":"修改成功",
            "success":1
            }
        return jsonify(data)

#%%




@bp.route('/admin_log_list/', methods=['GET', 'POST'])
@login_required
@admin_auth #p.310
def admin_log_list():
    
    '''
    if request.method == 'GET':
        return render_template('admin/admin_system_log.html')
    '''
    
    if request.method == 'GET':
        list=[]
        data={}
        admin_logs=db.session.query(Admin_Log).filter(Admin_Log.id > 0).all()
        for v in admin_logs:
            user=db.session.query(Users).filter(Users.uid == v.admin_id).first()
            data={
                'id':v.id,
                'operate':v.operate,
                'ip':v.ip,
                'add_time':v.add_time,
                'user_name':user.username}
            list.append(data)
        return render_template('admin/admin_system_log.html', list=list)
    
    


@bp.route('/admin_log_del/', methods=['GET', 'POST'])
def admin_log_del():
    id=int(request.values.get('aid'))
    comment1=db.session.query(Admin_Log).filter_by(id=id).first()
    db.session.delete(comment1)
    db.session.commit()
    
    list=[]
    data={}
    admin_logs=db.session.query(Admin_Log).filter(Admin_Log.id >0).all()
    
    for v in admin_logs:
        user=db.session.query(Users).filter(Users.uid == v.admin_id).first()
        data={
            'id':v.id,
            'operate':v.operate,
            'ip':v.ip,
            'add_time':v.add_time,
            'user_name':user.username}
        list.append(data)
    return render_template('admin/admin_system_log.html', list=list)
   




@bp.route('/system_log_all_del/', methods=['POST'])
def system_log_all_del():
    list1=[]
    id=str(request.values.get('aid'))
    id=id.strip(',').split(',')
    adminlog=db.session.query(Admin_Log).filter(Admin_Log.id.in_(id)).all()
    for v in adminlog:
        db.session.delete(v)
        db.session.commit()
    data={
        "msg":"修改成功",
        "success":1}
    
    return jsonify(data)
    

#%%

@bp.route('/admin_add_permission/', methods=['GET','POST'])
def admin_add_permission():
    if request.method == 'GET':
        auths=Auth.query.order_by(Auth.id.desc()).all()
        
        list=[]
        data={}
        for cat in auths:
            data=dict(id=cat.id,
                      parent_id=cat.parent_id,
                      name=cat.name)
            list.append(data)
        
        data=build_auth_tree(list,0,0)
        html=build_auth_table(data, parent_title='頂級菜單')
        return render_template('admin/admin_add_permission.html',
                               message=html)
    else:
        forms=Checek_Auth(request.form)
        if forms.validate():
            datas=forms.data
            auth1=Auth(
                name=datas['name'],
                url=datas['url'],
                parent_id=datas['parent_id'],
                status=datas['status']
                )
            db.session.add(auth1)
            db.session.commit()
            data={
                "msg":"提交成功",
                "status":"200"}
        else:
            data={
                "msg":"表單驗證失敗",
                "status":"202"}
    return jsonify(data)
            




@bp.route('/admin_permission/')
def admin_permission():
    page=int(request.args.get('page',1))
    paginate=Auth.query.order_by(Auth.id.desc()).paginate(page,4)
    arts=paginate.items
    return render_template('admin/admin_permission.html',
                           paginate=paginate, arts=arts)


@bp.route('/admin_edit_permission/', methods=['GET','POST'])
def admin_edit_permission():
    if request.method == 'GET':
        auths=Auth.query.order_by(Auth.id.desc()).all()
        print('auths')
        print(auths)
        
        list=[]
        data={}
        for cat in auths:
            data=dict(id=cat.id,
                      parent_id=cat.parent_id,
                      name=cat.name)
            list.append(data)
        
        data=build_auth_tree(list,0,0)
        html=build_auth_table(data, parent_title='頂級菜單')
        id=request.args.get('id') 
        #print('id: ')
        #print(id)
        if id != None:
            id=int(id)
            global auth1
            auth1=db.session.query(Auth).filter(Auth.id == id).first()
        #print(auth1)
        data={
            "msg":"參數獲取成功",
            "status":"200"}
        return render_template('admin/admin_edit_permission.html',
                               message=html, data=auth1)
    else:
        forms=Checek_Auth(request.form)
        if forms.validate():
            datas=forms.data
            
            url=request.form.get('url')
            id=int(request.values.get('id'))
        
            #auth1=db.session.query(Auth).filter(id == id).first()

            db.session.query(Auth).filter_by(id=id).update({Auth.name:datas['name'],
                                                            Auth.url:datas['url'],
                                                            Auth.parent_id:datas['parent_id'],
                                                            Auth.status:datas['status']})

            db.session.commit()
            data={
                "msg":"提交成功",
                "status":"200"}
        else:
            data={
                "msg":"表單驗證失敗",
                "status":"202"}
    return jsonify(data)




@bp.route('/admin_del_permission/', methods=['POST'])
def admin_del_permission():
    if request.method == 'POST':
        id=int(request.values.get('id'))

        if id:
            auth1=db.session.query(Auth).filter(Auth.id==id).first()

            db.session.delete(auth1)
            db.session.commit()
            data={
                "msg":"刪除成功",
                "status":"200"}
            return jsonify(data)
        else:
            data={
                "msg":"id參數不合法",
                "status":"202"}
            return jsonify(data)
            

#%%


@bp.route('/admin_add_role/', methods=['GET','POST'])
def admin_add_role():
    if request.method == 'GET':
        auths=Auth.query.order_by(Auth.id.desc()).all()
        
        list=[]
        data={}
        for cat in auths:
            data=dict(id=cat.id,
                      parent_id=cat.parent_id,
                      name=cat.name)
            list.append(data)
        
        data=build_auth_tree(list,0,0)
        html=build_auth_table(data, parent_title='頂級菜單')
        return render_template('admin/admin_add_role.html',
                               message=html)
    if request.method == 'POST':
        form=Checek_Role(request.form)

        if form.validate():
            datas=form.data
            auths=datas['auths']
            name=datas['name']
            description=datas['description']
            insert=Role(auths=auths,
                        name=name,
                        description=description
                        )
            db.session.add(insert)
            db.session.commit()
            data={
                "msg":"提交成功",
                "status":"200"}
            return jsonify(data)
        else:
            data={
                "msg":"表單驗證失敗",
                "status":"202"}
            return jsonify(data)





@bp.route('/admin_role_list', methods=['GET', 'POST'])
def admin_role_list():
    if request.method == 'GET':
        list=[]
        data={}
        roles=db.session.query(Role).all()
        count=db.session.query(func.count(Role.id)).scalar()
        for i in roles:
            admin=db.session.query(Users).filter(Users.role_id == i.id).first()
            if admin == None:
                admin="暫無"
            else:
                admin=admin.username
            data={
                'id':i.id,
                'name':i.name,
                'description':i.description,
                'admin':admin}
            list.append(data)
        
        return render_template('admin/admin_role.html',
                               roles=list, count=count)




@bp.route('/admin_edit_role/', methods=['GET','POST'])
def admin_edit_role():
    if request.method == 'GET':
        auths=Auth.query.order_by(Auth.id.desc()).all()
        
        list=[]
        data={}
        for cat in auths:
            data=dict(id=cat.id,
                      parent_id=cat.parent_id,
                      name=cat.name)
            list.append(data)
        
        data=build_auth_tree(list,0,0)
        html=creat_auth_table(data, parent_title='頂級菜單')
        id=request.args.get("id", '')
        if id:
            global role
            role=db.session.query(Role).filter(Role.id == id).first()
        return render_template('admin/admin_edit_role.html',
                               message=html, role=role)
    if request.method == 'POST':
        form=Checek_Role(request.form)
        if form.validate():
            datas=form.data
            auths=datas['auths']
            name=datas['name']
            description=datas['description']
            
            id=request.values.get('id')
            db.session.query(Role).filter_by(id=id).update({Role.auths:auths,
                                                            Role.name:name,
                                                            Role.description:description})
            db.session.commit()
            data={
                "msg":"提交成功",
                "status":"200"}
            return jsonify(data)



@bp.route('/admin_del_role/', methods=['POST'])
def admin_del_role():
    if request.method == 'POST':
        id=request.values.get('id')
        role=db.session.query(Role).filter(Role.id==id).first()
        db.session.delete(role)
        db.session.commit()
        data={
            'msg':"已刪除",
            'success':200}
        return jsonify(data)
    
#%%




@bp.route('/')
def index():
    return render_template('admin/login.html')
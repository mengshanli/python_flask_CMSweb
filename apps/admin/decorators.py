#https://stackoverflow.com/questions/308999/what-does-functools-wraps-do
#https://www.maxlist.xyz/2019/12/07/python-decorator/

#encoding:utf-8

from functools import wraps
from flask import session, redirect, url_for 

import config

from .models import Users, Role, Auth
from flask import request

def login_required(func):
    print('required')
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('enter')
        print(session.get('user_id'))
        if session.get(config.ADMIN_USER_ID):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('admin.login'))
    return wrapper 

#%%

def admin_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id=session.get(config.ADMIN_USER_ID)
        admin=Users.query.join(Role).filter(Role.id == Users.role_id,
                            Users.uid == user_id).first()
        
        auths=admin.jq_role.auths
        auths_list1=auths.split(",")
        auths_list2=[]
        
        for i, val in enumerate(auths_list1):
            auths_list2.append(int(val))
        #print(auths_list2) #具有權限的id

        auths_list3=[]
        auth_list=Auth.query.all()
        for i in auth_list:
            for v in auths_list2:
                if v == i.id:
                    auths_list3.append(i.url)
        #print(auths_list3) #具有權限的url
                    
        rule=str(request.url_rule) # 目前要拜訪的url
        #print('rule')
        #print(rule)
        if rule not in auths_list3:
            return '您沒有權限訪問'
        return func(*args, **kwargs)
    return wrapper
        
        
    
    
    
    
    
    
    
    
    
    
    
    
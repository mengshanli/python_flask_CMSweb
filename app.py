#https://www.codegrepper.com/code-examples/whatever/The+session+is+unavailable+because+no+secret+key+was+set.+Set+the+secret_key+on+the+application+to+something+unique+and+secret.


#encoding:utf-8
from flask import Flask

from apps.admin import bp as admin_bp
from apps.common import bp as common_bp
from apps.front import bp as front_bp

from exts import db

from apps.ueditor import bp as editor_bp

def create_app():
    app=Flask(__name__)
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(front_bp) #url_prefix='/test'
    
    app.register_blueprint(editor_bp)
    
    app.config.from_object('config')
    
    db.init_app(app)
    return app

'''
@app.route('/')
def hello_world():
    return 'hello falsk'
'''

if __name__ == '__main__':
    app=create_app()
    app.secret_key = 'super secret key' # book_revise
    app.run(host='127.0.0.1', port=8000, debug=True)
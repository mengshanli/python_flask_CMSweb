import os

DEBUG=True
DB_USERNAME=''
DB_PASSWROD=''
DB_HOST='127.0.0.1'
DB_PORT='5500'
DB_NAME=''

DB_URI='mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % \
        (DB_USERNAME, DB_PASSWROD, DB_HOST, DB_PORT, DB_NAME)

SQLALCHEMY_DATABASE_URI=DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS=False

#SECRET_KEY = os.urandom(24)


ADMIN_USER_ID='HEBOANHERE'
MEMBER_USER_ID='MEMBERREGISTER'



UEDITOR_UPLOAD_PATH=os.path.join(os.path.dirname(__file__), 'static', 'images')
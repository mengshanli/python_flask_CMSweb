from flask import g, session
import config
from .views import bp
from .models import Users

@bp.before_request 
def before_request():
    print("request")
    print(config.ADMIN_USER_ID)
    print(config.ADMIN_USER_ID in session)
    if config.ADMIN_USER_ID in session:
        print('yes')
        user_id=session.get(config.ADMIN_USER_ID)
        print(user_id)
        user=Users.query.get(user_id) #uid?
        print(user.username)
        if user:
            g.admin_user=user.username
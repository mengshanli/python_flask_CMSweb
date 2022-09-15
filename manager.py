#https://stackoverflow.com/questions/68527489/cant-import-migratecommand-from-flask-migrate
#https://www.cnblogs.com/rgcLOVEyaya/p/RGC_LOVE_YAYA_383days.html

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app
from exts import db
from apps.admin import models as admin_models

app=create_app()
manager=Manager(app)
Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
@manager.option('-e', '--email', dest='email')

def create_user(username, password, email):
    user=admin_models.Users(username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()
    print('data added success')
    
if __name__ =='__main__':
    manager.run()
    
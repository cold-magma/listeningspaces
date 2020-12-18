from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO,send,emit,join_room,leave_room

import os

db = SQLAlchemy()
app = None
socketio = SocketIO()

def create_app():
    global app
    app = Flask(__name__)

    app.config['SECRET_KEY'] = str(os.environ['SECRET_KEY'])

    app.config['SQLALCHEMY_DATABASE_URI'] = str(os.environ['DATABASE_URL'])

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    from .auth import auth
    app.register_blueprint(auth)

    from .main import main
    app.register_blueprint(main)

    socketio.init_app(app)
    
    return app
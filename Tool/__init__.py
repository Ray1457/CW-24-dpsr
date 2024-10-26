from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO  # Import SocketIO
import os

app = Flask(__name__, template_folder='./templates')  # Corrected the typo in 'templates'

# Configuration for the SQLAlchemy database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # It's good practice to disable this
app.secret_key = 'JHINGALALA HUR HUR'

# Initialize the database, migration tool, and socket IO
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)  # Initialize SocketIO

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


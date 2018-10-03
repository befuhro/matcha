from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

# Creating app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# Linking to the instance config
app.config.from_pyfile('config.py')

# Load bootstrap renderer
Bootstrap(app)
socketio = SocketIO(app)


# Bind views
import matcha.views
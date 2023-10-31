import os
from flask import Flask, make_response, request, jsonify
import datetime
from flask import Flask, send_from_directory, url_for
from sqlalchemy import MetaData
from werkzeug.security import generate_password_hash, check_password_hash
from .models import *
from flask_restx import Api, Resource, Namespace, fields
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
import datetime
import uuid
from flask_cors import CORS
from flask_marshmallow import Marshmallow


from flask_sqlalchemy import SQLAlchemy
import secrets


app = Flask(__name__, static_url_path='/static', static_folder='photos')

# Configure Flask-Uploads for image uploads
app.config['UPLOADED_PHOTOS_DEST'] = 'photos'  # Folder to store uploaded images

# Setup app configs
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)




CORS(app)

ma = Marshmallow(app)
migrate = Migrate(app, db)
api = Api(app)
ma = Marshmallow(app)

from api import routes, models

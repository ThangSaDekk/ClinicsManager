from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'fasdoadfnasdof@5#$%#$sadnas'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:thang123@localhost/privateclinics?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app=app)
login = LoginManager(app=app)
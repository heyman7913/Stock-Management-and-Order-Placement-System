from flask import Flask, render_template, abort, request
import os
from pathlib import Path
import json
from flask_sqlalchemy import SQLAlchemy

DATABASE = "DATABASE"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
HOST = "HOST"
PORT = "PORT"
NAME = "NAME"

# ========================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
app = Flask(__name__)

# SqlAlchemy Database Configuration With Mysql
try:
    with open(os.path.join(PROJECT_DIR, "documents", "secret.json")) as secret:
        data = json.load(secret)
        DB_CON = "mysql://{user_name}:password:{password}@{host}:{port}/{database}".format(
            user_name=data[DATABASE][USERNAME],
            password=data[DATABASE][PASSWORD],
            host=data[DATABASE][HOST],
            port=data[DATABASE][PORT],
            database=data[DATABASE][NAME],
        )
except Exception as e:
    print(str(e))
    raise KeyboardInterrupt
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_CON
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

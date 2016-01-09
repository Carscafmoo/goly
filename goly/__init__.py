from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('goly.cfg')

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

import goly.routes
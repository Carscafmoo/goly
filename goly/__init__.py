import sys
from flask import Flask
app = Flask(__name__)
if ('unittest' in sys.modules.keys()):
    app.config.from_pyfile('goly-test.cfg')
else:
    app.config.from_pyfile('goly.cfg')

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

import goly.routes.users
import goly.routes.goals
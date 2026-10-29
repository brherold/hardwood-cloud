from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Set the path for the SQLite database
database_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'basketball.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

@app.route('/')
def index():
    # Read SQL query from file
    with open(os.path.join(os.path.dirname(__file__), 'Queries', 'teamRoster.sql'), 'r') as file:
        sql_query = file.read()

    # Execute the query
    result = db.session.execute(sql_query)

    # Fetch all rows
    data = result.fetchall()

    # Render template and pass the data to frontend
    return render_template('index.html', data=data)

index()

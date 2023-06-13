#import required modules
import os
import psycopg2
from flask import Flask,render_template,request,url_for,flash, session,redirect
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash


# Load environmental variables from .env file
load_dotenv()

# Access your variables
secret_key = os.environ.get('SECRET_KEY')
database_url = os.environ.get('DATABASE_URL')

#intialized the app name
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/database_name'
db = SQLAlchemy(app)

#models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# Create Database Tables
db.create_all()

@app.route('/')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html',username=session['username'])
    else:
        return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)
#import required modules
import os
#import psycopg2
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
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)
app.secret_key = secret_key
app.app_context().push()
#models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    password = db.Column(db.String(300), nullable=False)

    def __init__(self, username, password,email):
        self.username = username
        self.email = email
        self.password = password
        

# Create Database Tables
db.create_all()

# Route to create a new post for a user
@app.route('/register', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

#protected
@app.route('/')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html',username=session['username'])
    else:
        return redirect(url_for('login'))
    
# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            flash('Login successful')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

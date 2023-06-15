#import required modules
import os
#import psycopg2
from flask import Flask,render_template,request,url_for,flash, session,redirect,jsonify
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
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
    posts = db.relationship('Post', backref='user',lazy=True)
    profile = db.relationship('Profile', backref='user')

    def __init__(self, username, password,email):
        self.username = username
        self.email = email
        self.password = password

#Profile
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer)
    profession = db.Column(db.String(100))
    country = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    bio = db.Column(db.Text)
    user_no = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, firstname, lastname,email,age,profession,country,bio):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.age = age
        self.profession = profession
        self.country = country
        self.bio = bio


#library
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    author =  db.Column(db.String(100))
    title = db.Column(db.String(50))
    year = db.Column(db.Integer)
    added_date = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    def __init__(self,category, author,title,year):
        self.category = category
        self.author = author
        self.title = title
        self.year = year

    def serialize(self):
        return {
            'id':self.id,
            'category': self.category,
            'author': self.author,
            'title': self.title,
            'year':self.year
        }
# Posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post')

    def __init__(self,title,content):
        self.content = content
        self.title = title
#comments
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    commented_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __init__(self,content):
        self.content = content

# Create Database Tables

db.create_all()
#======================================Methods starts here====================================#

#===============User Auth===================#
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
#===============End of User Auth===================#

#===============Library===================#
#Get all books
@app.route('/library')
def get_books():
    books = Books.query.all()
    return render_template('library.html',books=books)

#Get Api books
@app.route('/books', methods=['GET'])
def api_get_books():
    books = Books.query.all()
    serialized_books = [book.serialize() for book in books]
    return jsonify(serialized_books),200

#get one particular book
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    books = Books.query.filter_by(id=book_id).first()
    if books:
        serialized_books = books.serialize()
        return jsonify(serialized_books),200    
    return jsonify({"message": "Book not found"}), 404


# create a new Book
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    category = data.get('category')
    author = data.get('author')
    title = data.get('title')
    year = data.get('year')
    new_book = Books(category=category,author=author,title=title,year=year)

    db.session.add(new_book)
    db.session.commit()

    return jsonify(new_book.serialize()),201

#update book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Books.query.filter_by(id=book_id).first()
    if book:
        data = request.get_json()
        category = data.get('category')
        author = data.get('author')
        title = data.get('title')
        year = data.get('year')

        book.category = category
        book.author = author
        book.title = title
        book.year = year

        db.session.commit()

        return jsonify(book.serialize())
    return jsonify({'message': 'User not found'}), 404

#delete book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_books(book_id):
    book = Books.query.filter_by(id=book_id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted'})
    return jsonify({'message': 'Book not found'}), 404
#===============End of Library===================#
#import required modules
import os
import psycopg2
from flask import Flask,render_template,request,url_for,flash, session
from dotenv import load_dotenv


# Load environmental variables from .env file
load_dotenv()
#intialized the app name
app = Flask(__name__)

# Access your variables
secret_key = os.environ.get('SECRET_KEY')
database_url = os.environ.get('DATABASE_URL')
import requests
from flask import Flask, request, render_template, redirect, url_for, Response, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/BookStore"
app.config['SECRET_KEY'] = 'very_strong_secret_key'
mongo = PyMongo(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id: str):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    user = mongo.db.users.find_one({"_id": user_id})
    if user:
        return User(user_id)
    return None

def is_strong_password(password: str) -> bool:
    if len(password) < 8: 
        return False 
    if not re.search(r"[A-Z]", password): 
        return False 
    if not re.search(r"[a-z]", password): 
        return False 
    if not re.search(r"[0-9]", password): 
        return False 
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): 
        return False 
    return True

@app.route('/register', methods=['GET', 'POST'])
def register() -> Response:
    if request.method == 'POST':
        username: str = request.form['username']
        password: str = request.form['password']
        if not is_strong_password(password): 
            flash("Password must be at least 8 characters long and include uppercase and lowercase letters, numbers, and special characters.") 
            return render_template('register.html')
        user = mongo.db.users.find_one({'_id': username})
        if user:
            return render_template('register.html', message="User already exists. Please log in.")
        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({'_id': username, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login() -> Response:
    if request.method == 'POST':
        username: str = request.form['username']
        password: str = request.form['password']
        user = mongo.db.users.find_one({'_id': username})
        if user and check_password_hash(user['password'], password):
            login_user(User(username))
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message="Invalid username or password. Please try again.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard() -> Response:
    subscriptions = mongo.db.subscriptions.find({'email': current_user.id})
    return render_template('dashboard.html', subscriptions=subscriptions)

@app.route('/')
def home() -> Response:
    return render_template("home.html")

@app.route('/search')
def search() -> Response:
    url: str = "https://openlibrary.org/search.json?q="
    fields: str = "&fields=title,author_name,first_publish_year,key"
    query: Optional[str] = request.args.get('query')
    sort_order: Optional[str] = request.args.get('sort')

    try:
        response = requests.get(url + query.replace(" ", "+") + fields + "&sort=" + sort_order)
        response.raise_for_status()
        json_data = response.json()['docs']
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

    expected_keys = ['author_name', 'first_publish_year', 'title']
    html_content: str = ""
    for item in json_data:
        book_info: str = "<div class='book'>"
        for key in expected_keys:
            value = item.get(key, 'Unknown')
            if isinstance(value, list):
                value = ', '.join(value)
            formatted_key = key.title().replace("_", " ")
            book_info += f"<strong>{formatted_key}:</strong> {value}<br>"
        book_info += "</div>"
        html_content += book_info

    if response.json()['numFound'] == 0:
        html_content = "<p>No results found for your search!</p>"

    return render_template("results.html", html_content=html_content, query=query)

@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe() -> Response:
    if request.method == 'POST':
        title: str = request.form['title']
        email: str = current_user.id
        mongo.db.subscriptions.insert_one({'email': email, 'title': title})
        return render_template("thank_you.html")
    else:
        title: str = request.args.get('title', 'Unknown Title')
        return render_template('subscribe.html', title=title)

if __name__ == '__main__':
    app.run(debug=True)

import requests
from flask import Flask, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/BookStore"
app.config['SECRET_KEY'] = 'very_strong_secret_key'
mongo = PyMongo(app)
login_manager = LoginManager() 
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({"_id": user_id})
    if user:
        return User(user_id) 
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({'_id': username})
        if user:
            return render_template('register.html', message="User already exists. Please log in.")
        mongo.db.users.insert_one({'_id': username, 'password': password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({'_id': username})
        if user:
            user = mongo.db.users.find_one({'_id': username, 'password': password})
            login_user(User(username))
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message="User does not exists. Please register.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    subscriptions = mongo.db.subscriptions.find({'email': current_user.id})
    return render_template('dashboard.html', subscriptions=subscriptions)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/search')
def search():
    url = "https://openlibrary.org/search.json?q="
    fields = "&fields=title,author_name,first_publish_year,key"
    query = request.args.get('query')
    sort_order = request.args.get('sort')

    try:
        response = requests.get(url + query.replace(" ", "+") + fields + "&sort=" + sort_order)
        response.raise_for_status()
        json_data = response.json()['docs']
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

    expected_keys = ['author_name', 'first_publish_year', 'title']
    html_content = ""
    for item in json_data:
        book_info = "<div class='book'>"
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
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        title = request.form['title']
        mongo.db.subscriptions.insert_one({'email': email, 'title': title})
        return render_template("thank_you.html")
    else:
        title = request.args.get('title', 'Unknown Title')
        return render_template('subscribe.html', title=title)

if __name__ == '__main__':
    app.run(debug=True)
    
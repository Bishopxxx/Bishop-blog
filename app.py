from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)   

app.config['SECRET_KEY'] = 'secret key'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# db.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(20), unique=False, nullable=False)
    lastname = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



@app.route('/')
def home():
    return render_template("home.html")

@app.route('/signup')
def register():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile')
def profile():
    return render_template('about.html')

@app.route('/logout')
def logout():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/termsandprivacy')
def termsandprivacy():
    return render_template('terms.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
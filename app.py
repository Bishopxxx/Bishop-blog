from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user, login_user, LoginManager, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)   

app.config['SECRET_KEY'] = 'secret key'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.init_app(app)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(20), unique=False, nullable=False)
    lastname = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Create(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_created}')"

@app.route('/')
def home():
    posts = Create.query.order_by(Create.date_created.desc()).all()
    return render_template("home.html", posts=posts)

@app.route("/post/<int:id>")
def single_post(id):
    posts = Create.query.get_or_404(id)
    return render_template ("post.html", posts=posts, user=current_user)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        password = request.form.get("password")
        password1 = request.form.get("password1")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email address already exists.", category="error")
            return redirect(url_for("signup"))
        elif password != password1:
            flash("Passwords don't match", category="error")
        else:
            
            new_user = User(email=email, firstname=firstname, lastname=lastname, username=username, password=generate_password_hash(password, method='sha256'))

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
            
    return render_template("signup.html", user=current_user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user)
                return redirect (url_for("home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

        
    return render_template("login.html", user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return render_template('home.html')

@app.route('/create', methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author = current_user.username

        post = Create(title=title, content=content, author=author)

        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("create.html", user=current_user)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    title_to_edit = Create.query.get_or_404(id)
    post_to_update = Create.query.get_or_404(id)
    if request.method == "POST":
        title_to_edit.title = request.form.get("title")
        post_to_update.text = request.form.get("text")
        try:
            db.session.commit()
            return redirect(url_for("home"))
        except:
            flash("There was a problem updating that post.", category="error")
    return render_template("edit.html", post_to_update=post_to_update, title_to_edit=title_to_edit)


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    post = Create.query.get_or_404(id)
    
    try:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("home"))
    except:
        flash ("There was a problem deleting that post.", category="error")


@app.route('/profile')
def profile():
    return render_template('about.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/post/<int:id>')
def post(id):
    post = Create.query.get_or_404(id)
    return render_template('post.html', post=post)



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
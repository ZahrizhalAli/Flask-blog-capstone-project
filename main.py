from flask import Flask, render_template, redirect, url_for, flash, request, abort
from functools import wraps
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from forms import CreatePostForm, RegisterForm, LoginForm
import datetime
import smtplib
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "sqlite:///posts.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# response = requests.get("https://api.npoint.io/b45a3d3518ef5f96d0e6")
# data = response.json()
OWN_EMAIL = "blabla@gmail.com"
OWN_PASSWORD = "blablabla@123"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


# CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    children = relationship('BlogPost', back_populates="author")

    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class BlogPost(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    # bidirectional one-to-many
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = relationship('User', back_populates="children")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# db.create_all()


@app.route('/')
def home():
    data = db.session.query(BlogPost).all()
    return render_template("index.html", all_post=data)


# AUTHENTICATION
@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        if User.query.filter_by(email=register_form.email.data).first():
            flash('User already registered.')
            return redirect(url_for('login'))
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=register_form.email.data, password=hashed_password, name=register_form.name.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template("register.html", form=register_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        get_user = User.query.filter_by(email=login_form.email.data).first()
        if get_user:
            user_pass = get_user.password
            check = check_password_hash(user_pass, login_form.password.data)
            if check:
                user_pass = ""
                login_user(get_user)
                return redirect(url_for("home"))
            else:
                flash("Password wrong.")
                return redirect(url_for("login"))
        else:
            flash("User not found. Please register first.")
            return redirect(url_for("login"))
    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/blog/<int:blog_id>")
def get_blog(blog_id):
    data = BlogPost.query.filter_by(id=blog_id).first()

    return render_template("post.html", p=data)


@app.route('/edit/<int:blog_id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_post(blog_id):
    data = BlogPost.query.get(blog_id)
    post_form = CreatePostForm(
        title=data.title,
        subtitle=data.subtitle,
        img_url=data.img_url,
        author=data.author.name,
        body=data.body
    )
    if post_form.validate_on_submit():
        data.title = post_form.title.data
        data.subtitle = post_form.subtitle.data
        data.img_url = post_form.img_url.data
        data.body = post_form.body.data
        db.session.commit()
        return redirect(url_for("get_blog", blog_id=blog_id))
    return render_template('make-post.html', form=post_form)


@app.route('/new-post', methods=['POST', 'GET'])
@login_required
@admin_only
def new_post():
    post_form = CreatePostForm()
    title = post_form.title.data
    subtitle = post_form.subtitle.data
    img_url = post_form.img_url.data
    body = post_form.body.data
    x = datetime.datetime.now()
    month = x.strftime("%B")
    year = x.strftime("%Y")
    day = x.strftime("%d")
    date = f"{month} {day}, {year}"
    if post_form.validate_on_submit():
        new_entry = BlogPost(title=title, subtitle=subtitle, author_id=current_user.id, img_url=img_url, body=body, date=date)
        db.session.add(new_entry)
        db.session.commit()
        return redirect('/')
    return render_template("make-post.html", form=post_form)


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == "POST":
        dat = request.form
        print(dat['email'])
        print(dat['name'])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)


@app.route('/delete/<int:blog_id>', methods=['POST', 'GET'])
@login_required
@admin_only
def delete_post(blog_id):
    book_to_delete = BlogPost.query.get(blog_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)

# import bleach


# strips invalid tags/attributes
# def strip_invalid_html(content):
#     allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
#                     'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
#                     'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
#                     'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
#                     'thead', 'tr', 'tt', 'u', 'ul']
#
#     allowed_attrs = {
#         'a': ['href', 'target', 'title'],
#         'img': ['src', 'alt', 'width', 'height'],
#     }
#
#     cleaned = bleach.clean(content,
#                            tags=allowed_tags,
#                            attributes=allowed_attrs,
#                            strip=True)
#
#     return cleaned


## use strip_invalid_html-function before saving body
# body = strip_invalid_html(article.body.data)

## you can test the code by using strong-tag
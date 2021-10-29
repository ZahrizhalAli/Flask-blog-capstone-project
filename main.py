from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import requests
import smtplib
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# response = requests.get("https://api.npoint.io/b45a3d3518ef5f96d0e6")
# data = response.json()
OWN_EMAIL = "blabla@gmail.com"
OWN_PASSWORD = "blablabla@123"


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

# db.create_all()


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    # body = StringField("Blog Content", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def home():
    data = db.session.query(BlogPost).all()
    return render_template("index.html", all_post=data)


@app.route("/blog/<int:blog_id>")
def get_blog(blog_id):
    data = BlogPost.query.filter_by(id=blog_id).first()

    return render_template("post.html", p=data)


@app.route('/edit/<int:blog_id>', methods=['GET', 'POST'])
def edit_post(blog_id):
    data = BlogPost.query.get(blog_id)
    post_form = CreatePostForm(
        title=data.title,
        subtitle=data.subtitle,
        img_url=data.img_url,
        author=data.author,
        body=data.body
    )
    if post_form.validate_on_submit():
        data.title = post_form.title.data
        data.subtitle = post_form.subtitle.data
        data.img_url = post_form.img_url.data
        data.author = post_form.author.data
        data.body = post_form.body.data
        db.session.commit()
        return redirect(url_for("get_blog", blog_id=blog_id))
    return render_template('make-post.html', form=post_form)


@app.route('/new-post', methods=['POST', 'GET'])
def new_post():
    post_form = CreatePostForm()
    title = post_form.title.data
    subtitle = post_form.subtitle.data
    author = post_form.author.data
    img_url = post_form.img_url.data
    body = post_form.body.data
    x = datetime.datetime.now()
    month = x.strftime("%B")
    year = x.strftime("%Y")
    day = x.strftime("%d")
    date = f"{month} {day}, {year}"
    if post_form.validate_on_submit():
        new_entry = BlogPost(title=title, subtitle=subtitle, author=author, img_url=img_url, body=body, date=date)
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
def delete_post(blog_id):
    book_to_delete = BlogPost.query.get(blog_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)

# import bleach


## strips invalid tags/attributes
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
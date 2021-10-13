from flask import Flask, render_template
import requests

app = Flask(__name__)

response = requests.get("https://api.npoint.io/b45a3d3518ef5f96d0e6")
data = response.json()

@app.route('/')
def home():

    return render_template("index.html", posts=data)


@app.route("/post/<int:blog_id>")
def get_post(blog_id):

    return render_template("post.html", post=data, blog_id=blog_id)


if __name__ == "__main__":
    app.run(debug=True)

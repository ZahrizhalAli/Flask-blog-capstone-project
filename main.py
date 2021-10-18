from flask import Flask, render_template
import requests

app = Flask(__name__)

response = requests.get("https://api.npoint.io/b45a3d3518ef5f96d0e6")
data = response.json()


@app.route('/')
def home():
    return render_template("index.html", all_post=data)




@app.route("/blog/<int:blog_id>")
def get_blog(blog_id):
    select_data = None
    for n in data:
        if n['id'] == blog_id:
            select_data = n

    return render_template("post.html", p=select_data)


if __name__ == "__main__":
    app.run(debug=True)

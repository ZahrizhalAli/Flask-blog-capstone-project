from flask import Flask, render_template, request
import requests
import smtplib

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


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == "POST":
        data = request.form
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)


if __name__ == "__main__":
    app.run(debug=True)

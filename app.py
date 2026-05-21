from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "HireNest is a modern job portal platform that connects job seekers with employers, making hiring faster, smarter, and more efficient through a seamless digital experience...."


if __name__ == "__main__":
    app.run(debug=True)

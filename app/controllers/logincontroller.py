from flask import render_template
class LoginController:
    def login(self):
        return render_template("login.html")
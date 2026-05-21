from flask import render_template
class ForgetpasswordController:
    def password(self):
        return render_template("forgetpassword.html")
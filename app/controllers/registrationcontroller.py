from flask import render_template
class RegistrationController:
    def registration(self):
        return render_template("registration.html")
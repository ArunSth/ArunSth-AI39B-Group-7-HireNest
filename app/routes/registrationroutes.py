from flask import Blueprint, render_template

class RegistrationRoutes:
    def __init__(self):
        self.blueprint = Blueprint('registration', __name__)

    def registration(self):
        @self.blueprint.route('/register')
        def register():
            return render_template('registration.html')
            
        return self.blueprint
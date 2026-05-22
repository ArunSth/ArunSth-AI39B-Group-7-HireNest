from flask import Blueprint, render_template

class LoginRoutes:
    def __init__(self):
        # Create a Flask Blueprint named 'login'
        self.blueprint = Blueprint('login', __name__)

    def login(self):
        @self.blueprint.route('/')
        def index():
            # Renders base.html as your homepage/login interface
            return render_template('base.html')
            
        return self.blueprint
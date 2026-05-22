from flask import Blueprint, render_template

class ForgetPasswordRoutes:
    def __init__(self):
        self.blueprint = Blueprint('forget_password', __name__)

    def forget_password(self):
        @self.blueprint.route('/forget-password')
        def forget():
            return render_template('forgetpassword.html')
            
        return self.blueprint
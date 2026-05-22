from flask import Blueprint, redirect, url_for

class LogoutRoutes:
    def __init__(self):
        self.blueprint = Blueprint('logout', __name__)

    def logout(self):
        @self.blueprint.route('/logout')
        def process_logout():
            # Clears sessions here if needed, then redirects home
            return redirect(url_for('login.index'))
            
        return self.blueprint
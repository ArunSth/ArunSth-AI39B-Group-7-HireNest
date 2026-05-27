from flask import Blueprint, redirect, url_for, session, flash, make_response


class LogoutRoutes:
    def __init__(self):
        self.blueprint = Blueprint('logout', __name__)

    def logout(self):
        @self.blueprint.route('/logout')
        def process_logout():
            session.pop('user_id', None)
            session.pop('email', None)
            session.pop('role', None)
            session.pop('name', None)
            session.clear()
            session.modified = True

            flash('You have been logged out successfully.', 'success')

            response = make_response(redirect(url_for('login.index')))
            response.delete_cookie('session')
            return response

        return self.blueprint
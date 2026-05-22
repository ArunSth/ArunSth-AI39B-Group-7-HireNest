from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.modals.user import UserModel


class RegistrationRoutes:
    def __init__(self):
        self.blueprint = Blueprint('registration', __name__)

    def registration(self):
        @self.blueprint.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                phone = request.form.get('phone', '').strip()
                email = request.form.get('email', '').strip().lower()
                password = request.form.get('password', '')

                if not email or not password:
                    msg = 'Email and password are required.'
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'status': 'error', 'message': msg}), 400
                    flash(msg, 'error')
                    return render_template('registration.html')

                # split name into first/last
                first_name, last_name = (name.split(' ', 1) + [None])[:2]

                # check existing user
                existing = UserModel.get_by_email(email)
                if existing:
                    msg = 'An account with that email already exists.'
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'status': 'error', 'message': msg}), 409
                    flash(msg, 'error')
                    return render_template('registration.html')

                try:
                    UserModel.create(email=email, password=password,
                                     first_name=first_name, last_name=last_name)
                except Exception:
                    msg = 'Failed to create account. Please try again later.'
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'status': 'error', 'message': msg}), 500
                    flash(msg, 'error')
                    return render_template('registration.html')

                success_msg = 'Welcome — your account was created successfully.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'status': 'ok', 'message': success_msg, 'redirect': url_for('login.index')}), 201
                flash(success_msg, 'success')
                return redirect(url_for('login.index'))

            return render_template('registration.html')

        return self.blueprint

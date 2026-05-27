from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.modals.user import UserModel


class LoginRoutes:
    def __init__(self):
        self.blueprint = Blueprint('login', __name__)

    def login(self):
        @self.blueprint.route('/')
        def index():
            # If already logged in, redirect to appropriate dashboard
            if 'user_id' in session:
                role = session.get('role')
                if role == 'employer':
                    return redirect(url_for('employer.profile'))
                elif role == 'job_seeker':
                    return redirect(url_for('job_seeker.profile'))
            return render_template('base.html')

        @self.blueprint.route('/login', methods=['GET', 'POST'])
        def login_page():
            # Standalone login page (GET)
            if request.method == 'GET':
                if 'user_id' in session:
                    role = session.get('role')
                    if role == 'employer':
                        return redirect(url_for('employer.profile'))
                    return redirect(url_for('job_seeker.profile'))
                return render_template('login_page.html')

            # POST — handle login form submission (also used by AJAX from modal)
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            if not email or not password:
                msg = 'Email and password are required.'
                if is_ajax:
                    return jsonify({'status': 'error', 'message': msg}), 400
                flash(msg, 'error')
                return render_template('login_page.html')

            # Verify credentials
            user = UserModel.get_by_email(email)
            if not user or not UserModel.verify_password(email, password):
                msg = 'Invalid email or password.'
                if is_ajax:
                    return jsonify({'status': 'error', 'message': msg}), 401
                flash(msg, 'error')
                return render_template('login_page.html')

            # Set session
            session['user_id'] = user['User_id']
            session['email'] = user['Email']
            session['role'] = user.get('Role', 'job_seeker')
            session['name'] = f"{user.get('First_name', '')} {user.get('Last_name', '') or ''}".strip()

            role = session['role']
            if role == 'employer':
                redirect_url = url_for('employer.profile')
            else:
                redirect_url = url_for('job_seeker.profile')

            if is_ajax:
                return jsonify({'status': 'ok', 'message': 'Login successful!', 'redirect': redirect_url}), 200

            return redirect(redirect_url)

        return self.blueprint

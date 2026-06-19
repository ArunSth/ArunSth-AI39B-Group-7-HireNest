from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.modals.user import UserModel


class RegistrationRoutes:
    def __init__(self):
        self.blueprint = Blueprint('registration', __name__)

    def registration(self):
        @self.blueprint.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                # Support both modal field names (user-name) and standalone page names (name)
                name = (request.form.get('name') or request.form.get('user-name') or '').strip()
                phone = (request.form.get('phone') or request.form.get('user-phone') or '').strip()
                email = (request.form.get('email') or request.form.get('user-email') or '').strip().lower()
                password = request.form.get('password') or request.form.get('user-password') or ''
                # Role comes from hidden input: 'job_seeker' or 'employer'
                role = request.form.get('role', 'job_seeker').strip()
                if role not in ('job_seeker', 'employer'):
                    role = 'job_seeker'

                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

                if not email or not password:
                    msg = 'Email and password are required.'
                    if is_ajax:
                        return jsonify({'status': 'error', 'message': msg}), 400
                    flash(msg, 'error')
                    return render_template('registration.html')

                # Split name into first/last
                parts = name.split(' ', 1)
                first_name = parts[0] if parts else None
                last_name = parts[1] if len(parts) > 1 else None

                # Check for existing user
                existing = UserModel.get_by_email(email)
                if existing:
                    msg = 'An account with that email already exists.'
                    if is_ajax:
                        return jsonify({'status': 'error', 'message': msg}), 409
                    flash(msg, 'error')
                    return render_template('registration.html')

                try:
                    UserModel.create(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=role,
                    )
                except Exception:
                    msg = 'Failed to create account. Please try again later.'
                    if is_ajax:
                        return jsonify({'status': 'error', 'message': msg}), 500
                    flash(msg, 'error')
                    return render_template('registration.html')

                # Auto-login after successful registration
                user = UserModel.get_by_email(email)
                if user:
                    session['user_id'] = user['User_id']
                    session['email'] = user['Email']
                    session['role'] = user.get('Role', role)
                    session['name'] = f"{first_name or ''} {last_name or ''}".strip()

                if role == 'employer':
                    redirect_url = url_for('employer.profile')
                else:
                    redirect_url = url_for('job_seeker.dashboard')

                success_msg = 'Welcome to HireNest! Your account was created successfully.'
                if is_ajax:
                    return jsonify({'status': 'ok', 'message': success_msg, 'redirect': redirect_url}), 201
                flash(success_msg, 'success')
                return redirect(redirect_url)

            return render_template('registration.html')

        return self.blueprint

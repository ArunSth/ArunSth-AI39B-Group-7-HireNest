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
                   return redirect(url_for('employer.dashboard'))
               elif role == 'job_seeker':
                   return redirect(url_for('job_seeker.dashboard'))
               elif role == 'admin':
                   # Fixed endpoint name
                   return redirect(url_for('admin.admin_dashboard'))
           return render_template('base.html')
       @self.blueprint.route('/login', methods=['GET', 'POST'])
       def login_page():
           # Standalone login page (GET)
           if request.method == 'GET':
               if 'user_id' in session:
                   role = session.get('role')
                   if role == 'employer':
                       return redirect(url_for('employer.profile'))
                   elif role == 'admin':
                       # Fixed endpoint name
                       return redirect(url_for('admin.admin_dashboard'))
                   return redirect(url_for('job_seeker.dashboard'))
               return render_template('login_page.html')
           # POST — handle login form submission
           email = request.form.get('email', '').strip().lower()
           password = request.form.get('password', '')
           selected_role = request.form.get('role', 'job_seeker').strip()
           is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
           # Validate role selection
           if selected_role not in ('job_seeker', 'employer', 'admin'):
               selected_role = 'job_seeker'
           if not email or not password:
               msg = 'Email and password are required.'
               if is_ajax: return jsonify({'status': 'error', 'message': msg}), 400
               flash(msg, 'error')
               return render_template('login_page.html')
           # Verify credentials
           user = UserModel.get_by_email(email)
           if not user or not UserModel.verify_password(email, password):
               msg = 'Invalid email or password.'
               if is_ajax: return jsonify({'status': 'error', 'message': msg}), 401
               flash(msg, 'error')
               return render_template('login_page.html')
           # Validate that selected role matches user's account role
           user_role = user.get('Role', 'job_seeker')
           if selected_role != user_role:
               msg = f'This account is registered as a {user_role.replace("_", " ")}. Please select the correct role.'
               if is_ajax: return jsonify({'status': 'error', 'message': msg}), 401
               flash(msg, 'error')
               return render_template('login_page.html')
           # STRICT ADMIN VALIDATION: Only allow specific email for admin
           if user_role == 'admin' and email != 'admin@hirenest':
               msg = 'Unauthorized access attempt.'
               if is_ajax: return jsonify({'status': 'error', 'message': msg}), 403
               flash(msg, 'error')
               return render_template('login_page.html')
           # Set session
           session['user_id'] = user['User_id']
           session['email'] = user['Email']
           session['role'] = user_role
           session['name'] = f"{user.get('First_name', '')} {user.get('Last_name', '') or ''}".strip()
           # Determine redirect URL based on role
           if user_role == 'employer':
               redirect_url = url_for('employer.dashboard')
           elif user_role == 'admin':
               # FIXED: Changed from 'admin.dashboard' to 'admin.admin_dashboard'
               redirect_url = url_for('admin.admin_dashboard')
           else:
               redirect_url = url_for('job_seeker.dashboard')
           if is_ajax:
               return jsonify({'status': 'ok', 'message': 'Login successful!', 'redirect': redirect_url}), 200
           return redirect(redirect_url)
       return self.blueprint
from flask import Blueprint, jsonify, render_template, request
from app.controllers.forgetpasswordcontroller import ForgetpasswordController


class ForgetPasswordRoutes:
    def __init__(self):
        self.blueprint = Blueprint('forget_password', __name__)

    def forget_password(self):

        @self.blueprint.route('/forget-password', methods=['GET'])
        def forget():
            return render_template('forgetpassword.html')

        @self.blueprint.route('/forget-password/check-email', methods=['POST'])
        def check_email():
            data = request.get_json(silent=True) or {}
            email = (data.get('email') or '').strip().lower()
            if not email:
                return jsonify({'status': 'error', 'message': 'Email is required.'}), 400
            found, user = ForgetpasswordController.check_email(email)
            if found:
                return jsonify({'status': 'success', 'message': 'Email found.'}), 200
            return jsonify({'status': 'error', 'message': 'No account found with this email.'}), 404

        @self.blueprint.route('/forget-password/reset', methods=['POST'])
        def reset_password():
            data = request.get_json(silent=True) or {}
            email = (data.get('email') or '').strip().lower()
            new_password = data.get('new_password') or ''
            confirm_password = data.get('confirm_password') or ''
            success, message = ForgetpasswordController.reset_password(email, new_password, confirm_password)
            if success:
                return jsonify({'status': 'success', 'message': message}), 200
            return jsonify({'status': 'error', 'message': message}), 400

        return self.blueprint
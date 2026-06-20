import json
import unittest
from unittest.mock import patch

from flask import Blueprint, Flask

from app.routes.loginroutes import LoginRoutes


class TestLoginRoleValidation(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test-secret'

        employer_bp = Blueprint('employer', __name__)

        @employer_bp.route('/employer/dashboard')
        def dashboard():
            return 'employer dashboard'

        job_seeker_bp = Blueprint('job_seeker', __name__)

        @job_seeker_bp.route('/job-seeker/dashboard')
        def dashboard():
            return 'job seeker dashboard'

        admin_bp = Blueprint('admin', __name__)

        @admin_bp.route('/admin/dashboard')
        def admin_dashboard():
            return 'admin dashboard'

        self.app.register_blueprint(employer_bp)
        self.app.register_blueprint(job_seeker_bp)
        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(LoginRoutes().login())
        self.client = self.app.test_client()

    @patch('app.routes.loginroutes.UserModel.verify_password', return_value=True)
    @patch('app.routes.loginroutes.UserModel.get_by_email')
    def test_job_seeker_cannot_login_with_employer_account(self, mock_get_by_email, mock_verify_password):
        mock_get_by_email.return_value = {
            'User_id': 1,
            'Email': 'employer@example.com',
            'Role': 'employer',
            'First_name': 'Employer',
            'Last_name': 'User'
        }

        response = self.client.post(
            '/login',
            data={
                'email': 'employer@example.com',
                'password': 'secret123',
                'role': 'job_seeker'
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        self.assertEqual(response.status_code, 401)
        payload = response.get_json()
        self.assertEqual(
            payload['message'], 'Selected account type does not match this account.')

        with self.client.session_transaction() as session:
            self.assertNotIn('user_id', session)

    @patch('app.routes.loginroutes.UserModel.verify_password', return_value=True)
    @patch('app.routes.loginroutes.UserModel.get_by_email')
    def test_employer_cannot_login_with_job_seeker_account(self, mock_get_by_email, mock_verify_password):
        mock_get_by_email.return_value = {
            'User_id': 2,
            'Email': 'jobseeker@example.com',
            'Role': 'job_seeker',
            'First_name': 'Job',
            'Last_name': 'Seeker'
        }

        response = self.client.post(
            '/login',
            data={
                'email': 'jobseeker@example.com',
                'password': 'secret123',
                'role': 'employer'
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        self.assertEqual(response.status_code, 401)
        payload = response.get_json()
        self.assertEqual(
            payload['message'], 'Selected account type does not match this account.')

    @patch('app.routes.loginroutes.UserModel.verify_password', return_value=True)
    @patch('app.routes.loginroutes.UserModel.get_by_email')
    def test_admin_cannot_login_with_job_seeker_role(self, mock_get_by_email, mock_verify_password):
        mock_get_by_email.return_value = {
            'User_id': 3,
            'Email': 'admin@hirenest',
            'Role': 'admin',
            'First_name': 'Admin',
            'Last_name': 'User'
        }

        response = self.client.post(
            '/login',
            data={
                'email': 'admin@hirenest',
                'password': 'secret123',
                'role': 'job_seeker'
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        self.assertEqual(response.status_code, 401)
        payload = response.get_json()
        self.assertEqual(
            payload['message'], 'Selected account type does not match this account.')

    @patch('app.routes.loginroutes.UserModel.verify_password', return_value=True)
    @patch('app.routes.loginroutes.UserModel.get_by_email')
    def test_job_seeker_can_login_with_matching_role(self, mock_get_by_email, mock_verify_password):
        mock_get_by_email.return_value = {
            'User_id': 4,
            'Email': 'seeker@example.com',
            'Role': 'job_seeker',
            'First_name': 'Jane',
            'Last_name': 'Doe'
        }

        response = self.client.post(
            '/login',
            data={
                'email': 'seeker@example.com',
                'password': 'secret123',
                'role': 'job_seeker'
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['status'], 'ok')
        self.assertIn('/job-seeker', payload['redirect'])

    @patch('app.routes.loginroutes.UserModel.verify_password', return_value=True)
    @patch('app.routes.loginroutes.UserModel.get_by_email')
    def test_employer_can_login_with_matching_role(self, mock_get_by_email, mock_verify_password):
        mock_get_by_email.return_value = {
            'User_id': 5,
            'Email': 'employer@example.com',
            'Role': 'employer',
            'First_name': 'Employer',
            'Last_name': 'User'
        }

        response = self.client.post(
            '/login',
            data={
                'email': 'employer@example.com',
                'password': 'secret123',
                'role': 'employer'
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['status'], 'ok')
        self.assertIn('/employer/dashboard', payload['redirect'])

    @patch('app.routes.loginroutes.UserModel.verify_password', return_value=True)
    @patch('app.routes.loginroutes.UserModel.get_by_email')
    def test_admin_can_login_with_matching_role(self, mock_get_by_email, mock_verify_password):
        mock_get_by_email.return_value = {
            'User_id': 6,
            'Email': 'admin@hirenest',
            'Role': 'admin',
            'First_name': 'Admin',
            'Last_name': 'User'
        }

        response = self.client.post(
            '/login',
            data={
                'email': 'admin@hirenest',
                'password': 'secret123',
                'role': 'admin'
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['status'], 'ok')
        self.assertIn('/admin', payload['redirect'])


if __name__ == '__main__':
    unittest.main()

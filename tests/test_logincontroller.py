import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages
from app.routes.loginroutes import LoginRoutes


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    app.register_blueprint(LoginRoutes().login())

    employer_bp = Blueprint("employer", __name__)
    employer_bp.route("/employer/dashboard", endpoint="dashboard")(lambda: "employer dashboard")
    employer_bp.route("/employer/profile", endpoint="profile")(lambda: "employer profile")
    app.register_blueprint(employer_bp)

    admin_bp = Blueprint("admin", __name__)
    admin_bp.route("/admin/admin_dashboard", endpoint="admin_dashboard")(lambda: "admin dashboard")
    app.register_blueprint(admin_bp)

    seeker_bp = Blueprint("job_seeker", __name__)
    seeker_bp.route("/job_seeker/dashboard", endpoint="dashboard")(lambda: "job seeker dashboard")
    app.register_blueprint(seeker_bp)

    return app


class TestLoginController(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()

    @patch("app.routes.loginroutes.render_template")
    def test_get_page_load(self, mock_render):
        mock_render.return_value = "login_page"

        with self.app.test_request_context("/login", method="GET"):
            result = self.app.view_functions["login.login_page"]()

            self.assertEqual(result, "login_page")
            mock_render.assert_called_once_with("login_page.html")

    @patch("app.routes.loginroutes.render_template")
    @patch("app.routes.loginroutes.UserModel.verify_password")
    @patch("app.routes.loginroutes.UserModel.get_by_email")
    def test_valid_login_creates_session_and_redirects(self, mock_get_by_email, mock_verify_password, mock_render):
        mock_render.return_value = "login_page"
        mock_get_by_email.return_value = {
            "User_id": 7,
            "Email": "bob@example.com",
            "Role": "job_seeker",
            "First_name": "Bob",
            "Last_name": "Smith",
        }
        mock_verify_password.return_value = True

        with self.app.test_request_context("/login", method="POST", data={"email": "bob@example.com", "password": "secret", "role": "job_seeker"}):
            response = self.app.view_functions["login.login_page"]()

            self.assertEqual(response.status_code, 302)
            self.assertIn("/job_seeker/dashboard", response.location)
            self.assertEqual(session["user_id"], 7)
            self.assertEqual(session["email"], "bob@example.com")
            self.assertEqual(session["role"], "job_seeker")
            self.assertEqual(session["name"], "Bob Smith")

    @patch("app.routes.loginroutes.render_template")
    @patch("app.routes.loginroutes.UserModel.verify_password")
    @patch("app.routes.loginroutes.UserModel.get_by_email")
    def test_invalid_login_shows_error(self, mock_get_by_email, mock_verify_password, mock_render):
        mock_render.return_value = "login_page"
        mock_get_by_email.return_value = {
            "User_id": 7,
            "Email": "bob@example.com",
            "Role": "job_seeker",
            "First_name": "Bob",
            "Last_name": "Smith",
        }
        mock_verify_password.return_value = False

        with self.app.test_request_context("/login", method="POST", data={"email": "bob@example.com", "password": "wrongpass", "role": "job_seeker"}):
            result = self.app.view_functions["login.login_page"]()

            self.assertEqual(result, "login_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("error", "Invalid email or password."), flashes)
            self.assertFalse(session.get("user_id"))

    @patch("app.routes.loginroutes.render_template")
    def test_missing_email_shows_error(self, mock_render):
        mock_render.return_value = "login_page"

        with self.app.test_request_context("/login", method="POST", data={"email": "", "password": "secret", "role": "job_seeker"}):
            result = self.app.view_functions["login.login_page"]()

            self.assertEqual(result, "login_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("error", "Email and password are required."), flashes)
            self.assertFalse(session.get("user_id"))

    @patch("app.routes.loginroutes.render_template")
    def test_missing_password_shows_error(self, mock_render):
        mock_render.return_value = "login_page"

        with self.app.test_request_context("/login", method="POST", data={"email": "bob@example.com", "password": "", "role": "job_seeker"}):
            result = self.app.view_functions["login.login_page"]()

            self.assertEqual(result, "login_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("error", "Email and password are required."), flashes)
            self.assertFalse(session.get("user_id"))


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages
from app.routes.registrationroutes import RegistrationRoutes


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.config["ADMIN_SETTINGS"] = {"userRegistration": True}

    app.register_blueprint(RegistrationRoutes().registration())

    employer_bp = Blueprint("employer", __name__)
    employer_bp.route("/employer/profile", endpoint="profile")(lambda: "employer profile")
    app.register_blueprint(employer_bp)

    seeker_bp = Blueprint("job_seeker", __name__)
    seeker_bp.route("/job_seeker/dashboard", endpoint="dashboard")(lambda: "job seeker dashboard")
    app.register_blueprint(seeker_bp)

    return app


class TestRegistrationController(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()

    @patch("app.routes.registrationroutes.render_template")
    def test_registration_page_loads(self, mock_render):
        mock_render.return_value = "registration_page"

        with self.app.test_request_context("/register", method="GET"):
            result = self.app.view_functions["registration.register"]()

            self.assertEqual(result, "registration_page")
            mock_render.assert_called_once_with("registration.html")

    @patch("app.routes.registrationroutes.render_template")
    def test_registration_missing_email_shows_error(self, mock_render):
        mock_render.return_value = "registration_page"

        with self.app.test_request_context("/register", method="POST", data={"name": "Alice", "email": "", "password": "secret"}):
            result = self.app.view_functions["registration.register"]()
            self.assertEqual(result, "registration_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("error", "Email and password are required."), flashes)
            self.assertFalse(session.get("user_id"))

    @patch("app.routes.registrationroutes.render_template")
    def test_registration_missing_password_shows_error(self, mock_render):
        mock_render.return_value = "registration_page"

        with self.app.test_request_context("/register", method="POST", data={"name": "Alice", "email": "alice@example.com", "password": ""}):
            result = self.app.view_functions["registration.register"]()
            self.assertEqual(result, "registration_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("error", "Email and password are required."), flashes)
            self.assertFalse(session.get("user_id"))

    @patch("app.routes.registrationroutes.render_template")
    @patch("app.routes.registrationroutes.UserModel.get_by_email")
    def test_registration_duplicate_email_shows_error(self, mock_get_by_email, mock_render):
        mock_render.return_value = "registration_page"
        mock_get_by_email.return_value = {"User_id": 1, "Email": "alice@example.com"}

        with self.app.test_request_context("/register", method="POST", data={"name": "Alice", "email": "alice@example.com", "password": "secret"}):
            result = self.app.view_functions["registration.register"]()
            self.assertEqual(result, "registration_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("error", "An account with that email already exists."), flashes)
            self.assertFalse(session.get("user_id"))

    @patch("app.routes.registrationroutes.JobSeekerProfileModel.ensure_profile_exists")
    @patch("app.routes.registrationroutes.UserModel.create")
    @patch("app.routes.registrationroutes.UserModel.get_by_email")
    @patch("app.routes.registrationroutes.render_template")
    def test_registration_success_redirects(self, mock_render, mock_get_by_email, mock_create, mock_ensure_profile):
        mock_render.return_value = "registration_page"
        mock_get_by_email.side_effect = [None, {"User_id": 8, "Email": "alice@example.com", "Role": "job_seeker"}]

        with self.app.test_request_context("/register", method="POST", data={"name": "Alice Smith", "email": "alice@example.com", "password": "secret", "role": "job_seeker"}):
            response = self.app.view_functions["registration.register"]()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/job_seeker/dashboard", response.location)
            self.assertEqual(session["user_id"], 8)
            self.assertEqual(session["email"], "alice@example.com")
            self.assertEqual(session["role"], "job_seeker")
            self.assertEqual(session["name"], "Alice Smith")
            mock_create.assert_called_once()
            mock_ensure_profile.assert_called_once_with(8)

    @patch("app.routes.registrationroutes.render_template")
    @patch("app.routes.registrationroutes.UserModel.get_by_email")
    def test_registration_disabled_shows_error(self, mock_get_by_email, mock_render):
        mock_render.return_value = "registration_page"
        self.app.config["ADMIN_SETTINGS"]["userRegistration"] = False

        with self.app.test_request_context("/register", method="POST", data={"name": "Alice", "email": "alice@example.com", "password": "secret"}):
            result = self.app.view_functions["registration.register"]()
            self.assertEqual(result, "registration_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("error", "New user registration is currently disabled. Please try again later."), flashes)
            self.assertFalse(session.get("user_id"))


if __name__ == "__main__":
    unittest.main()

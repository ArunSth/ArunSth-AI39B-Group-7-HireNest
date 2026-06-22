import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages
from app.controllers.auth_controller import AuthController


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    bp = Blueprint("auth", __name__)
    bp.route("/", endpoint="home")(lambda: "home")
    bp.route("/login", endpoint="login")(lambda: "login")
    bp.route("/dashboard", endpoint="dashboard")(lambda: "dashboard")
    bp.route("/register", endpoint="register")(lambda: "register")
    bp.route("/profile", endpoint="profile")(lambda: "profile")
    app.register_blueprint(bp)
    return app


class TestAuthController(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()
        self.controller.user_model = MagicMock()

    @patch("app.controllers.auth_controller.render_template")
    def test_home_renders_base_template(self, mock_render):
        mock_render.return_value = "base_page"

        with self.app.test_request_context(method="GET"):
            result = self.controller.home()

        self.assertEqual(result, "base_page")
        mock_render.assert_called_once_with("base.html")

    @patch("app.controllers.auth_controller.render_template")
    def test_login_get_shows_login_form(self, mock_render):
        mock_render.return_value = "login_page"

        with self.app.test_request_context(method="GET"):
            result = self.controller.login()

        self.assertEqual(result, "login_page")
        mock_render.assert_called_once_with("login.html")

    @patch("app.controllers.auth_controller.render_template")
    def test_login_missing_fields_shows_error(self, mock_render):
        mock_render.return_value = "login_page"

        with self.app.test_request_context(method="POST", data={"email": "", "password": ""}):
            result = self.controller.login()
            self.assertEqual(result, "login_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Email and password are required."), flashes)

    @patch("app.controllers.auth_controller.User.from_db")
    @patch("app.controllers.auth_controller.render_template")
    def test_login_invalid_password_shows_error(self, mock_render, mock_from_db):
        mock_render.return_value = "login_page"
        self.controller.user_model.find_by.return_value = {
            "id": 1,
            "name": "Bob",
            "email": "bob@example.com",
            "role": "user",
        }
        fake_user = MagicMock()
        fake_user.check_password.return_value = False
        mock_from_db.return_value = fake_user

        with self.app.test_request_context(method="POST", data={"email": "bob@example.com", "password": "wrongpass"}):
            result = self.controller.login()
            self.assertEqual(result, "login_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Invalid email or password."), flashes)
            self.assertFalse(session.get("user_id"))

    @patch("app.controllers.auth_controller.User.from_db")
    def test_login_success_sets_session_and_redirects(self, mock_from_db):
        self.controller.user_model.find_by.return_value = {
            "id": 2,
            "name": "Bob",
            "email": "bob@example.com",
            "role": "user",
        }
        fake_user = MagicMock()
        fake_user.check_password.return_value = True
        mock_from_db.return_value = fake_user

        with self.app.test_request_context(method="POST", data={"email": "bob@example.com", "password": "secret1"}):
            response = self.controller.login()
            self.assertEqual(session["user_id"], 2)
            self.assertEqual(session["user_name"], "Bob")
            self.assertEqual(session["role"], "user")
            self.assertEqual(response.status_code, 302)
            self.assertIn("/", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Login successful!"), flashes)

    @patch("app.controllers.auth_controller.render_template")
    def test_register_get_shows_registration_form(self, mock_render):
        mock_render.return_value = "registration_page"

        with self.app.test_request_context(method="GET"):
            result = self.controller.register()

        self.assertEqual(result, "registration_page")
        mock_render.assert_called_once_with("registration.html")

    @patch("app.controllers.auth_controller.render_template")
    def test_register_missing_fields_shows_error(self, mock_render):
        mock_render.return_value = "registration_page"

        with self.app.test_request_context(method="POST", data={"name": "", "email": "", "password": ""}):
            result = self.controller.register()
            self.assertEqual(result, "registration_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "All fields are required."), flashes)

    @patch("app.controllers.auth_controller.User")
    def test_register_duplicate_email_redirects(self, mock_user_class):
        fake_user = MagicMock()
        fake_user.email_exists.return_value = True
        mock_user_class.return_value = fake_user

        with self.app.test_request_context(method="POST", data={"name": "Bob", "email": "taken@example.com", "password": "secret1"}):
            response = self.controller.register()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/register", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Email already exists."), flashes)
            fake_user.save.assert_not_called()

    @patch("app.controllers.auth_controller.User")
    def test_register_success_redirects_to_login(self, mock_user_class):
        fake_user = MagicMock()
        fake_user.email_exists.return_value = False
        mock_user_class.return_value = fake_user

        with self.app.test_request_context(method="POST", data={"name": "Alice", "email": "alice@example.com", "password": "secret1"}):
            response = self.controller.register()
            fake_user.save.assert_called_once()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Registration successful! Please login."), flashes)

    def test_logout_clears_session_and_redirects(self):
        with self.app.test_request_context():
            session["user_id"] = 99
            session["user_name"] = "Alice"
            session["role"] = "user"

            response = self.controller.logout()
            self.assertFalse(session.get("user_id"))
            self.assertFalse(session.get("user_name"))
            self.assertFalse(session.get("role"))
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Logged out successfully."), flashes)

    @patch("app.controllers.auth_controller.render_template")
    def test_dashboard_renders_admin_dashboard(self, mock_render):
        users = [{"id": 1, "name": "Bob"}]
        self.controller.user_model.find_all.return_value = users
        mock_render.return_value = "dashboard_page"

        with self.app.test_request_context():
            result = self.controller.dashboard()

        self.assertEqual(result, "dashboard_page")
        mock_render.assert_called_once_with("admin_dashboard.html", users=users)

    @patch("app.controllers.auth_controller.render_template")
    def test_profile_get_renders_profile_page(self, mock_render):
        mock_render.return_value = "profile_page"
        self.controller.user_model.find_by_id.return_value = {"id": 10, "name": "Alice"}

        with self.app.test_request_context():
            session["user_id"] = 10
            result = self.controller.profile()

        self.assertEqual(result, "profile_page")
        mock_render.assert_called_once_with("job_seeker_profile.html", user={"id": 10, "name": "Alice"})

    @patch("app.controllers.auth_controller.User.from_db")
    @patch("app.controllers.auth_controller.render_template")
    def test_profile_post_wrong_current_password(self, mock_render, mock_from_db):
        mock_render.return_value = "profile_page"
        self.controller.user_model.find_by_id.return_value = {"id": 10, "name": "Alice", "password": "oldpass"}
        stored_user = MagicMock()
        stored_user.check_password.return_value = False
        mock_from_db.return_value = stored_user

        with self.app.test_request_context(method="POST", data={"name": "Alice", "email": "alice@example.com", "current_password": "wrongpass", "new_password": "newsecret"}):
            session["user_id"] = 10
            result = self.controller.profile()
            self.assertEqual(result, "profile_page")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Current password is incorrect."), flashes)
            mock_from_db.assert_called_once()

    @patch("app.controllers.auth_controller.User")
    def test_profile_post_updates_successfully(self, mock_user_class):
        fake_user = MagicMock()
        fake_user.email_exists.return_value = False
        mock_user_class.return_value = fake_user
        self.controller.user_model.find_by_id.return_value = {"id": 10, "name": "Alice"}

        with self.app.test_request_context(method="POST", data={"name": "Alice", "email": "alice@example.com", "current_password": "", "new_password": ""}):
            session["user_id"] = 10
            response = self.controller.profile()
            fake_user.update_profile.assert_called_once_with(10, update_password=False)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/profile", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Profile updated successfully!"), flashes)


if __name__ == "__main__":
    unittest.main()

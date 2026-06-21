import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session

from app.controllers.auth_controller import AuthController


class TestAuthController(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = "test-secret"
        self.app.config["TESTING"] = True

    @patch("app.controllers.auth_controller.render_template")
    def test_home_renders_base_template(self, mock_render_template):
        mock_render_template.return_value = "rendered-base"
        controller = AuthController()

        with self.app.test_request_context("/", method="GET"):
            result = controller.home()

        self.assertEqual(result, "rendered-base")
        mock_render_template.assert_called_once_with("base.html")

    @patch("app.controllers.auth_controller.redirect")
    @patch("app.controllers.auth_controller.url_for")
    def test_login_redirects_logged_in_non_admin(self, mock_url_for, mock_redirect):
        mock_url_for.return_value = "/home"
        mock_redirect.return_value = "redirect-home"
        controller = AuthController()

        with self.app.test_request_context("/login", method="GET"):
            session["user_id"] = 1
            session["role"] = "user"
            result = controller.login()

        self.assertEqual(result, "redirect-home")
        mock_url_for.assert_called_once_with("auth.home")

    @patch("app.controllers.auth_controller.redirect")
    @patch("app.controllers.auth_controller.url_for")
    def test_login_redirects_logged_in_admin(self, mock_url_for, mock_redirect):
        mock_url_for.return_value = "/dashboard"
        mock_redirect.return_value = "redirect-dashboard"
        controller = AuthController()

        with self.app.test_request_context("/login", method="GET"):
            session["user_id"] = 1
            session["role"] = "admin"
            result = controller.login()

        self.assertEqual(result, "redirect-dashboard")
        mock_url_for.assert_called_once_with("auth.dashboard")

    @patch("app.controllers.auth_controller.flash")
    @patch("app.controllers.auth_controller.render_template")
    def test_login_post_missing_credentials_renders_login(self, mock_render_template, mock_flash):
        mock_render_template.return_value = "login-page"
        controller = AuthController()

        with self.app.test_request_context("/login", method="POST", data={}):
            result = controller.login()

        self.assertEqual(result, "login-page")
        mock_render_template.assert_called_once_with("login.html")
        mock_flash.assert_called_once_with("Email and password are required.", "danger")

    @patch("app.controllers.auth_controller.User")
    @patch("app.controllers.auth_controller.AuthController.flash_and_redirect")
    def test_login_post_valid_user_redirects_home(self, mock_flash_and_redirect, mock_user_class):
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_user_class.from_db.return_value = mock_user
        mock_user_model = MagicMock()
        mock_user_model.find_by.return_value = {"id": 11, "name": "Alice", "role": "user"}
        mock_user_class.return_value = mock_user_model
        mock_flash_and_redirect.return_value = "flash-home"
        controller = AuthController()

        with self.app.test_request_context("/login", method="POST", data={"email": "alice@example.com", "password": "password123"}):
            result = controller.login()

        self.assertEqual(result, "flash-home")
        self.assertEqual(session["user_id"], 11)
        self.assertEqual(session["user_name"], "Alice")
        self.assertEqual(session["role"], "user")

    @patch("app.controllers.auth_controller.flash")
    @patch("app.controllers.auth_controller.render_template")
    def test_login_post_invalid_credentials_shows_error(self, mock_render_template, mock_flash):
        mock_render_template.return_value = "login-page"
        controller = AuthController()
        controller.user_model = MagicMock()
        controller.user_model.find_by.return_value = None

        with self.app.test_request_context("/login", method="POST", data={"email": "bad@example.com", "password": "wrong"}):
            result = controller.login()

        self.assertEqual(result, "login-page")
        mock_render_template.assert_called_once_with("login.html")
        mock_flash.assert_called_once_with("Invalid email or password.", "danger")

    @patch("app.controllers.auth_controller.redirect")
    @patch("app.controllers.auth_controller.url_for")
    def test_register_redirects_logged_in_user(self, mock_url_for, mock_redirect):
        mock_url_for.return_value = "/dashboard"
        mock_redirect.return_value = "redirect-dashboard"
        controller = AuthController()

        with self.app.test_request_context("/register", method="GET"):
            session["user_id"] = 16
            result = controller.register()

        self.assertEqual(result, "redirect-dashboard")
        mock_url_for.assert_called_once_with("auth.dashboard")

    @patch("app.controllers.auth_controller.flash")
    @patch("app.controllers.auth_controller.render_template")
    @patch("app.controllers.auth_controller.User")
    def test_register_post_missing_fields_renders_registration(self, mock_user_class, mock_render_template, mock_flash):
        mock_render_template.return_value = "registration-page"
        controller = AuthController()
        controller.user_model = MagicMock()

        with self.app.test_request_context("/register", method="POST", data={"name": "", "email": "", "password": ""}):
            result = controller.register()

        self.assertEqual(result, "registration-page")
        mock_render_template.assert_called_once_with("registration.html")
        mock_flash.assert_called_once_with("All fields are required.", "danger")

    @patch("app.controllers.auth_controller.AuthController.flash_and_redirect")
    @patch("app.controllers.auth_controller.User")
    def test_register_post_success_saves_user_and_redirects_login(self, mock_user_class, mock_flash_and_redirect):
        mock_user = MagicMock()
        mock_user.email_exists.return_value = False
        mock_user_class.return_value = mock_user
        mock_flash_and_redirect.return_value = "redirect-login"
        controller = AuthController()

        with self.app.test_request_context("/register", method="POST", data={"name": "Bob", "email": "bob@example.com", "password": "secret12"}):
            result = controller.register()

        self.assertEqual(result, "redirect-login")
        mock_user.save.assert_called_once()

    @patch("app.controllers.auth_controller.AuthController.flash_and_redirect")
    def test_logout_clears_session_and_redirects(self, mock_flash_and_redirect):
        mock_flash_and_redirect.return_value = "redirect-login"
        controller = AuthController()

        with self.app.test_request_context("/logout", method="GET"):
            session["user_id"] = 99
            session["user_name"] = "Tester"
            result = controller.logout()

        self.assertEqual(result, "redirect-login")
        self.assertFalse(session)

    @patch("app.controllers.auth_controller.render_template")
    def test_dashboard_renders_admin_dashboard_with_users(self, mock_render_template):
        mock_render_template.return_value = "dashboard-page"
        controller = AuthController()
        controller.user_model = MagicMock()
        controller.user_model.find_all.return_value = [{"id": 1, "name": "Alice"}]

        with self.app.test_request_context("/dashboard", method="GET"):
            result = controller.dashboard()

        self.assertEqual(result, "dashboard-page")
        mock_render_template.assert_called_once_with("admin_dashboard.html", users=[{"id": 1, "name": "Alice"}])

    @patch("app.controllers.auth_controller.render_template")
    def test_profile_get_renders_profile(self, mock_render_template):
        mock_render_template.return_value = "profile-page"
        controller = AuthController()
        controller.user_model = MagicMock()
        controller.get_current_user_id = MagicMock(return_value=5)
        controller.user_model.find_by_id.return_value = {"id": 5, "name": "Jane"}

        with self.app.test_request_context("/profile", method="GET"):
            result = controller.profile()

        self.assertEqual(result, "profile-page")
        mock_render_template.assert_called_once_with("job_seeker_profile.html", user={"id": 5, "name": "Jane"})

    @patch("app.controllers.auth_controller.flash")
    @patch("app.controllers.auth_controller.render_template")
    def test_profile_post_missing_name_or_email_shows_error(self, mock_render_template, mock_flash):
        mock_render_template.return_value = "profile-page"
        controller = AuthController()
        controller.get_current_user_id = MagicMock(return_value=5)
        controller.user_model = MagicMock()
        controller.user_model.find_by_id.return_value = {"id": 5, "name": "Jane"}

        with self.app.test_request_context("/profile", method="POST", data={"name": "", "email": ""}):
            result = controller.profile()

        self.assertEqual(result, "profile-page")
        mock_flash.assert_called_once_with("Name and email are required.", "danger")
        mock_render_template.assert_called_once_with("job_seeker_profile.html", user={"id": 5, "name": "Jane"})

    @patch("app.controllers.auth_controller.User")
    @patch("app.controllers.auth_controller.flash")
    @patch("app.controllers.auth_controller.render_template")
    def test_profile_post_incorrect_current_password(self, mock_render_template, mock_flash, mock_user_class):
        mock_render_template.return_value = "profile-page"
        controller = AuthController()
        controller.get_current_user_id = MagicMock(return_value=5)
        controller.user_model = MagicMock()
        controller.user_model.find_by_id.return_value = {"id": 5, "name": "Jane", "password": "hash"}
        stored_user = MagicMock()
        stored_user.check_password.return_value = False
        mock_user_class.from_db.return_value = stored_user

        with self.app.test_request_context("/profile", method="POST", data={"name": "Jane", "email": "jane@example.com", "current_password": "bad", "new_password": "newsecret"}):
            result = controller.profile()

        self.assertEqual(result, "profile-page")
        mock_flash.assert_called_once_with("Current password is incorrect.", "danger")
        mock_render_template.assert_called_once_with("job_seeker_profile.html", user={"id": 5, "name": "Jane", "password": "hash"})

    @patch("app.controllers.auth_controller.User")
    @patch("app.controllers.auth_controller.AuthController.flash_and_redirect")
    def test_profile_post_updates_profile_and_redirects(self, mock_flash_and_redirect, mock_user_class):
        mock_flash_and_redirect.return_value = "redirect-profile"
        controller = AuthController()
        controller.get_current_user_id = MagicMock(return_value=5)
        controller.user_model = MagicMock()
        controller.user_model.find_by_id.side_effect = [{"id": 5, "name": "Jane", "password": "hash"}, {"id": 5, "name": "Jane", "password": "hash"}]
        stored_user = MagicMock()
        stored_user.check_password.return_value = True
        mock_user_class.from_db.return_value = stored_user
        user_obj = MagicMock()
        mock_user_class.return_value = user_obj

        with self.app.test_request_context("/profile", method="POST", data={"name": "Jane", "email": "jane@example.com", "current_password": "correct", "new_password": "newsecret"}):
            result = controller.profile()

        self.assertEqual(result, "redirect-profile")
        user_obj.set_password.assert_called_once_with("newsecret")
        user_obj.update_profile.assert_called_once_with(5, update_password=True)
        self.assertEqual(session["user_name"], "Jane")


if __name__ == "__main__":
    unittest.main()

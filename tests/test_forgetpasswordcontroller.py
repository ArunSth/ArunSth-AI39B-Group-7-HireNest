import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.forgetpasswordroutes import ForgetPasswordRoutes
from app.controllers.forgetpasswordcontroller import ForgetpasswordController


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.register_blueprint(ForgetPasswordRoutes().forget_password())
    return app


class TestForgetPasswordController(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()

    @patch("app.routes.forgetpasswordroutes.render_template")
    def test_forgot_password_page_loads(self, mock_render):
        mock_render.return_value = "forget_password_page"

        with self.app.test_client() as client:
            response = client.get("/forget-password")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "forget_password_page")
        mock_render.assert_called_once_with("forgetpassword.html")

    @patch("app.routes.forgetpasswordroutes.ForgetpasswordController.check_email")
    def test_valid_email_submission(self, mock_check_email):
        mock_check_email.return_value = (True, {"User_id": 1, "Email": "alice@example.com"})

        with self.app.test_client() as client:
            response = client.post("/forget-password/check-email", json={"email": "alice@example.com"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "success", "message": "Email found."})
        mock_check_email.assert_called_once_with("alice@example.com")

    @patch("app.routes.forgetpasswordroutes.ForgetpasswordController.check_email")
    def test_invalid_email_submission(self, mock_check_email):
        mock_check_email.return_value = (False, None)

        with self.app.test_client() as client:
            response = client.post("/forget-password/check-email", json={"email": "unknown@example.com"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"status": "error", "message": "No account found with this email."})
        mock_check_email.assert_called_once_with("unknown@example.com")

    def test_missing_email_submission(self):
        with self.app.test_client() as client:
            response = client.post("/forget-password/check-email", json={"email": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"status": "error", "message": "Email is required."})

    @patch("app.routes.forgetpasswordroutes.ForgetpasswordController.reset_password")
    def test_reset_password_flow_success(self, mock_reset_password):
        mock_reset_password.return_value = (True, "Password reset successfully!")

        with self.app.test_client() as client:
            response = client.post(
                "/forget-password/reset",
                json={
                    "email": "alice@example.com",
                    "new_password": "newsecret123",
                    "confirm_password": "newsecret123",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "success", "message": "Password reset successfully!"})
        mock_reset_password.assert_called_once_with("alice@example.com", "newsecret123", "newsecret123")

    @patch("app.routes.forgetpasswordroutes.ForgetpasswordController.reset_password")
    def test_reset_password_flow_error(self, mock_reset_password):
        mock_reset_password.return_value = (False, "Passwords do not match.")

        with self.app.test_client() as client:
            response = client.post(
                "/forget-password/reset",
                json={
                    "email": "alice@example.com",
                    "new_password": "newsecret123",
                    "confirm_password": "different123",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"status": "error", "message": "Passwords do not match."})
        mock_reset_password.assert_called_once_with("alice@example.com", "newsecret123", "different123")


class TestForgetPasswordControllerLogic(unittest.TestCase):
    @patch("app.controllers.forgetpasswordcontroller.UserModel.get_by_email")
    def test_check_email_returns_true_for_existing_user(self, mock_get_by_email):
        mock_get_by_email.return_value = {"User_id": 1, "Email": "alice@example.com"}

        found, user = ForgetpasswordController.check_email("alice@example.com")

        self.assertTrue(found)
        self.assertEqual(user, {"User_id": 1, "Email": "alice@example.com"})

    @patch("app.controllers.forgetpasswordcontroller.UserModel.get_by_email")
    def test_check_email_returns_false_for_missing_user(self, mock_get_by_email):
        mock_get_by_email.return_value = None

        found, user = ForgetpasswordController.check_email("unknown@example.com")

        self.assertFalse(found)
        self.assertIsNone(user)

    @patch("app.controllers.forgetpasswordcontroller.UserModel.update_password")
    @patch("app.controllers.forgetpasswordcontroller.UserModel.get_by_email")
    def test_reset_password_success(self, mock_get_by_email, mock_update_password):
        mock_get_by_email.return_value = {"User_id": 1, "Email": "alice@example.com"}
        mock_update_password.return_value = True

        success, message = ForgetpasswordController.reset_password("alice@example.com", "newsecret123", "newsecret123")

        self.assertTrue(success)
        self.assertEqual(message, "Password reset successfully!")
        mock_update_password.assert_called_once_with("alice@example.com", "newsecret123")

    @patch("app.controllers.forgetpasswordcontroller.UserModel.get_by_email")
    def test_reset_password_rejects_missing_fields(self, mock_get_by_email):
        success, message = ForgetpasswordController.reset_password("alice@example.com", "", "")

        self.assertFalse(success)
        self.assertEqual(message, "Please fill in all fields.")
        mock_get_by_email.assert_not_called()

    @patch("app.controllers.forgetpasswordcontroller.UserModel.get_by_email")
    def test_reset_password_rejects_password_mismatch(self, mock_get_by_email):
        success, message = ForgetpasswordController.reset_password("alice@example.com", "secret1", "secret2")

        self.assertFalse(success)
        self.assertEqual(message, "Passwords do not match.")
        mock_get_by_email.assert_not_called()

    @patch("app.controllers.forgetpasswordcontroller.UserModel.get_by_email")
    def test_reset_password_rejects_short_password(self, mock_get_by_email):
        success, message = ForgetpasswordController.reset_password("alice@example.com", "short", "short")

        self.assertFalse(success)
        self.assertEqual(message, "Password must be at least 8 characters long.")
        mock_get_by_email.assert_not_called()

    @patch("app.controllers.forgetpasswordcontroller.UserModel.update_password")
    @patch("app.controllers.forgetpasswordcontroller.UserModel.get_by_email")
    def test_reset_password_reports_no_account(self, mock_get_by_email, mock_update_password):
        mock_get_by_email.return_value = None

        success, message = ForgetpasswordController.reset_password("unknown@example.com", "newsecret123", "newsecret123")

        self.assertFalse(success)
        self.assertEqual(message, "No account found with this email.")
        mock_update_password.assert_not_called()

    @patch("app.controllers.forgetpasswordcontroller.UserModel.get_by_email")
    @patch("app.controllers.forgetpasswordcontroller.UserModel.update_password")
    def test_reset_password_reports_update_failure(self, mock_update_password, mock_get_by_email):
        mock_get_by_email.return_value = {"User_id": 1, "Email": "alice@example.com"}
        mock_update_password.return_value = False

        success, message = ForgetpasswordController.reset_password("alice@example.com", "newsecret123", "newsecret123")

        self.assertFalse(success)
        self.assertEqual(message, "Something went wrong. Please try again.")
        mock_update_password.assert_called_once_with("alice@example.com", "newsecret123")


if __name__ == "__main__":
    unittest.main()

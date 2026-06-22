import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session, get_flashed_messages
from app.routes.subscription_routes import SubscriptionRoutes


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.register_blueprint(SubscriptionRoutes().subscription_routes())

    login_bp = MagicMock()
    # register a minimal login endpoint for url_for('login.index')
    from flask import Blueprint
    login_bp = Blueprint("login", __name__)
    login_bp.route("/login", endpoint="index")(lambda: "login")
    app.register_blueprint(login_bp)

    employer_bp = Blueprint("employer", __name__)
    employer_bp.route("/employer/profile", endpoint="profile")(lambda: "employer profile")
    app.register_blueprint(employer_bp)

    return app


def make_mock_db(employee_id=2):
    mock_cursor = MagicMock()
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"Employee_id": employee_id}
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


class TestSubscriptionController(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()

    @patch("app.routes.subscription_routes.render_template")
    @patch("app.routes.subscription_routes.SubscriptionController.get_active_subscription")
    @patch("app.routes.subscription_routes.SubscriptionController.get_all_plans")
    @patch("app.routes.subscription_routes.UserModel.get_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.ensure_default_plans")
    @patch("app.database.get_connection")
    def test_subscription_page_loads(
        self,
        mock_get_connection,
        mock_ensure_default_plans,
        mock_get_by_id,
        mock_get_all_plans,
        mock_get_active_subscription,
        mock_render,
    ):
        mock_render.return_value = "subscription_page"
        mock_get_by_id.return_value = {"User_id": 5, "Email": "boss@example.com"}
        mock_get_all_plans.return_value = [{"Plan_id": 1, "Name": "Basic"}]
        mock_get_active_subscription.return_value = None
        mock_get_connection.return_value = make_mock_db(employee_id=12)

        with self.app.test_request_context("/employer/subscription-plans", method="GET"):
            session["user_id"] = 5
            session["role"] = "employer"
            result = self.app.view_functions["subscriptions.plans"]()

        self.assertEqual(result, "subscription_page")
        mock_ensure_default_plans.assert_called_once()
        mock_get_by_id.assert_called_once_with(5)
        mock_get_all_plans.assert_called_once()
        mock_render.assert_called_once_with(
            "subscription_plans.html",
            user={"User_id": 5, "Email": "boss@example.com"},
            plans=[{"Plan_id": 1, "Name": "Basic"}],
            active_subscription=None,
        )

    @patch("app.routes.subscription_routes.render_template")
    @patch("app.routes.subscription_routes.SubscriptionController.get_active_subscription")
    @patch("app.routes.subscription_routes.SubscriptionController.get_all_plans")
    @patch("app.routes.subscription_routes.UserModel.get_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.ensure_default_plans")
    @patch("app.database.get_connection")
    def test_view_plans(self,
        mock_get_connection,
        mock_ensure_default_plans,
        mock_get_by_id,
        mock_get_all_plans,
        mock_get_active_subscription,
        mock_render,
    ):
        mock_render.return_value = "subscription_page"
        mock_get_by_id.return_value = {"User_id": 5, "Email": "boss@example.com"}
        mock_get_all_plans.return_value = [{"Plan_id": 1, "Name": "Pro"}]
        mock_get_active_subscription.return_value = {"Subscription_id": 10}
        mock_get_connection.return_value = make_mock_db(employee_id=7)

        with self.app.test_request_context("/employer/subscription-plans", method="GET"):
            session["user_id"] = 5
            session["role"] = "employer"
            response = self.app.view_functions["subscriptions.plans"]()

        self.assertEqual(response, "subscription_page")
        mock_get_active_subscription.assert_called_once_with(7)
        self.assertEqual(mock_get_all_plans.call_count, 1)

    @patch("app.routes.subscription_routes.flash")
    @patch("app.routes.subscription_routes.SubscriptionController.record_payment")
    @patch("app.routes.subscription_routes.SubscriptionController.create_subscription")
    @patch("app.routes.subscription_routes.SubscriptionController.get_plan_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.get_active_subscription")
    @patch("app.routes.subscription_routes.SubscriptionController.get_all_plans")
    @patch("app.routes.subscription_routes.UserModel.get_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.ensure_default_plans")
    @patch("app.database.get_connection")
    def test_select_plan_and_payment_success(
        self,
        mock_get_connection,
        mock_ensure_default_plans,
        mock_get_by_id,
        mock_get_all_plans,
        mock_get_active_subscription,
        mock_get_plan_by_id,
        mock_create_subscription,
        mock_record_payment,
        mock_flash,
    ):
        mock_get_by_id.return_value = {"User_id": 5, "Email": "boss@example.com"}
        mock_get_all_plans.return_value = [{"Plan_id": 1, "Name": "Premium", "Price": 50}]
        mock_get_active_subscription.return_value = None
        mock_get_plan_by_id.return_value = {"Plan_id": 1, "Name": "Premium", "Price": 50}
        mock_create_subscription.return_value = 99
        mock_record_payment.return_value = True
        mock_get_connection.return_value = make_mock_db(employee_id=3)

        with self.app.test_request_context("/employer/subscription-plans", method="POST", data={"plan_id": "1", "auto_renew": "on"}):
            session["user_id"] = 5
            session["role"] = "employer"
            response = self.app.view_functions["subscriptions.plans"]()

        self.assertEqual(response.status_code, 302)
        self.assertIn("/employer/subscription-plans", response.location)
        mock_flash.assert_called_once_with("Subscription purchased successfully.", "success")
        mock_get_plan_by_id.assert_called_once_with("1")
        mock_create_subscription.assert_called_once()
        mock_record_payment.assert_called_once_with(99, 3, 50, transaction_reference=None)

    @patch("app.routes.subscription_routes.flash")
    @patch("app.routes.subscription_routes.SubscriptionController.get_plan_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.get_active_subscription")
    @patch("app.routes.subscription_routes.SubscriptionController.get_all_plans")
    @patch("app.routes.subscription_routes.UserModel.get_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.ensure_default_plans")
    @patch("app.database.get_connection")
    def test_invalid_plan_shows_error(
        self,
        mock_get_connection,
        mock_ensure_default_plans,
        mock_get_by_id,
        mock_get_all_plans,
        mock_get_active_subscription,
        mock_get_plan_by_id,
        mock_flash,
    ):
        mock_get_by_id.return_value = {"User_id": 5, "Email": "boss@example.com"}
        mock_get_all_plans.return_value = [{"Plan_id": 2, "Name": "Standard"}]
        mock_get_active_subscription.return_value = None
        mock_get_plan_by_id.return_value = None
        mock_get_connection.return_value = make_mock_db(employee_id=4)

        with self.app.test_request_context("/employer/subscription-plans", method="POST", data={"plan_id": "999"}):
            session["user_id"] = 5
            session["role"] = "employer"
            response = self.app.view_functions["subscriptions.plans"]()

        self.assertEqual(response.status_code, 302)
        self.assertIn("/employer/subscription-plans", response.location)
        mock_flash.assert_called_once_with("Selected plan not found.", "error")
        mock_get_plan_by_id.assert_called_once_with("999")

    @patch("app.routes.subscription_routes.flash")
    @patch("app.routes.subscription_routes.SubscriptionController.get_active_subscription")
    @patch("app.routes.subscription_routes.SubscriptionController.get_all_plans")
    @patch("app.routes.subscription_routes.UserModel.get_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.ensure_default_plans")
    @patch("app.database.get_connection")
    def test_missing_plan_shows_error(
        self,
        mock_get_connection,
        mock_ensure_default_plans,
        mock_get_by_id,
        mock_get_all_plans,
        mock_get_active_subscription,
        mock_flash,
    ):
        mock_get_by_id.return_value = {"User_id": 5, "Email": "boss@example.com"}
        mock_get_all_plans.return_value = [{"Plan_id": 2, "Name": "Standard"}]
        mock_get_active_subscription.return_value = None
        mock_get_connection.return_value = make_mock_db(employee_id=4)

        with self.app.test_request_context("/employer/subscription-plans", method="POST", data={}):
            session["user_id"] = 5
            session["role"] = "employer"
            response = self.app.view_functions["subscriptions.plans"]()

        self.assertEqual(response.status_code, 302)
        self.assertIn("/employer/subscription-plans", response.location)
        mock_flash.assert_called_once_with("Please select a plan.", "error")

    @patch("app.routes.subscription_routes.flash")
    @patch("app.routes.subscription_routes.render_template")
    @patch("app.routes.subscription_routes.SubscriptionController.record_payment")
    @patch("app.routes.subscription_routes.SubscriptionController.create_subscription")
    @patch("app.routes.subscription_routes.SubscriptionController.get_plan_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.get_active_subscription")
    @patch("app.routes.subscription_routes.SubscriptionController.get_all_plans")
    @patch("app.routes.subscription_routes.UserModel.get_by_id")
    @patch("app.routes.subscription_routes.SubscriptionController.ensure_default_plans")
    @patch("app.database.get_connection")
    def test_payment_failure_path(
        self,
        mock_get_connection,
        mock_ensure_default_plans,
        mock_get_by_id,
        mock_get_all_plans,
        mock_get_active_subscription,
        mock_get_plan_by_id,
        mock_create_subscription,
        mock_record_payment,
        mock_render,
        mock_flash,
    ):
        mock_get_by_id.return_value = {"User_id": 5, "Email": "boss@example.com"}
        mock_get_all_plans.return_value = [{"Plan_id": 1, "Name": "Premium", "Price": 50}]
        mock_get_active_subscription.return_value = None
        mock_get_plan_by_id.return_value = {"Plan_id": 1, "Name": "Premium", "Price": 50}
        mock_create_subscription.return_value = None
        mock_record_payment.return_value = False
        mock_render.return_value = "subscription_page"
        mock_get_connection.return_value = make_mock_db(employee_id=3)

        with self.app.test_request_context("/employer/subscription-plans", method="POST", data={"plan_id": "1"}):
            session["user_id"] = 5
            session["role"] = "employer"
            response = self.app.view_functions["subscriptions.plans"]()

        self.assertEqual(response, "subscription_page")
        mock_flash.assert_called_once_with("Failed to purchase subscription. Please try again.", "error")
        mock_create_subscription.assert_called_once()

    @patch("app.routes.subscription_routes.flash")
    def test_redirects_for_non_employer(self, mock_flash):
        with self.app.test_request_context("/employer/subscription-plans", method="GET"):
            session.clear()
            response = self.app.view_functions["subscriptions.plans"]()

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        mock_flash.assert_called_once_with("Please log in as an employer to view subscription plans.", "error")


if __name__ == "__main__":
    unittest.main()

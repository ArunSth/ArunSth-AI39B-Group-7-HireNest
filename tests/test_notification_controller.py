import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from flask import Flask, Blueprint
from app.routes.notificationroutes import NotificationRoutes


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.register_blueprint(NotificationRoutes().notifications())

    login_bp = Blueprint("login", __name__)
    login_bp.route("/login", endpoint="index")(lambda: "login")
    app.register_blueprint(login_bp)

    messages_bp = Blueprint("messages", __name__)
    messages_bp.route("/messages/<int:conversation_id>", endpoint="conversation")(lambda conversation_id: f"conversation-{conversation_id}")
    app.register_blueprint(messages_bp)

    employer_bp = Blueprint("employer", __name__)
    employer_bp.route("/employer/dashboard", endpoint="dashboard")(lambda: "employer-dashboard")
    app.register_blueprint(employer_bp)

    return app


def make_valid_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 5


class TestNotificationControllerRoutes(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()

    @patch("app.routes.notificationroutes.render_template")
    @patch("app.routes.notificationroutes.NotificationModel.unread_count")
    @patch("app.routes.notificationroutes.NotificationModel.get_notifications")
    def test_notification_list_load(self, mock_get_notifications, mock_unread_count, mock_render):
        mock_render.return_value = "notifications_page"
        mock_get_notifications.return_value = [
            {"Notification_id": 1, "Title": "Test", "Message": "Hello"}
        ]
        mock_unread_count.return_value = 3

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/notifications")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "notifications_page")
        mock_render.assert_called_once()

    @patch("app.routes.notificationroutes.NotificationModel.mark_read")
    @patch("app.routes.notificationroutes.NotificationModel.get_notification")
    def test_mark_as_read(self, mock_get_notification, mock_mark_read):
        mock_mark_read.return_value = 1
        mock_get_notification.return_value = {"Notification_id": 1, "Type": "general", "Reference_id": None}

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post("/notifications/read/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "success", "updated": 1})
        mock_mark_read.assert_called_once_with(1, 5)

    @patch("app.routes.notificationroutes.NotificationModel.mark_read")
    def test_mark_as_read_invalid_notification(self, mock_mark_read):
        mock_mark_read.return_value = 0

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post("/notifications/read/999")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "error", "updated": 0})
        mock_mark_read.assert_called_once_with(999, 5)

    @patch("app.routes.notificationroutes.NotificationModel.get_notifications")
    @patch("app.routes.notificationroutes.NotificationModel.unread_count")
    def test_empty_notification_list(self, mock_unread_count, mock_get_notifications):
        mock_get_notifications.return_value = []
        mock_unread_count.return_value = 0

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/notifications/recent")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"notifications": [], "unread_count": 0})

    @patch("app.routes.notificationroutes.NotificationModel.get_notification")
    def test_open_invalid_notification_redirects(self, mock_get_notification):
        mock_get_notification.return_value = None

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/notifications/open/999")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/notifications", response.location)

    def test_redirect_behavior_for_unauthenticated_user(self):
        with self.app.test_client() as client:
            response = client.get("/notifications")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)


class TestNotificationControllerLogic(unittest.TestCase):
    @patch("app.controllers.notification_controller.NotificationModel.get_notifications")
    def test_fetch_recent_notifications_truncates(self, mock_get_notifications):
        mock_get_notifications.return_value = [
            {"Notification_id": i, "Title": f"Title {i}", "Created_at": datetime.now()} for i in range(12)
        ]

        result = __import__("app.controllers.notification_controller", fromlist=["NotificationController"]).NotificationController.fetch_recent_notifications(5)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["Notification_id"], 0)

    @patch("app.controllers.notification_controller.NotificationModel.mark_read")
    def test_mark_all_read_via_controller(self, mock_mark_read):
        mock_mark_read.return_value = 12
        result = __import__("app.controllers.notification_controller", fromlist=["NotificationController"]).NotificationController.mark_read(7, 5)
        self.assertEqual(result, 12)
        mock_mark_read.assert_called_once_with(7, 5)


if __name__ == "__main__":
    unittest.main()

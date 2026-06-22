import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint
from app.routes.messageroutes import MessageRoutes
from app.controllers.message_controller import MessageController


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.register_blueprint(MessageRoutes().messages())

    login_bp = Blueprint("login", __name__)
    login_bp.route("/login", endpoint="index")(lambda: "login")
    app.register_blueprint(login_bp)

    return app


def make_valid_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["role"] = "job_seeker"


class TestMessageControllerRoutes(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()

    @patch("app.routes.messageroutes.render_template")
    @patch("app.routes.messageroutes.MessageController.unread_count")
    @patch("app.routes.messageroutes.MessageController.mark_read")
    @patch("app.routes.messageroutes.MessageController.fetch_conversation")
    @patch("app.routes.messageroutes.UserModel.get_online_status")
    @patch("app.routes.messageroutes.UserModel.get_by_id")
    @patch("app.routes.messageroutes.MessageController.fetch_conversations")
    @patch("app.routes.messageroutes.UserModel.update_last_active")
    def test_inbox_page_loads(
        self,
        mock_update_last_active,
        mock_fetch_conversations,
        mock_get_by_id,
        mock_get_online_status,
        mock_fetch_conversation,
        mock_mark_read,
        mock_unread_count,
        mock_render,
    ):
        mock_render.return_value = "inbox_page"
        mock_fetch_conversations.return_value = [
            {"user": {"User_id": 10, "First_name": "Alice", "Last_name": "Smith", "Role": "employer"}}
        ]
        mock_get_by_id.return_value = {"User_id": 10, "First_name": "Alice", "Last_name": "Smith"}
        mock_get_online_status.return_value = {"online": True}
        mock_fetch_conversation.return_value = [{"Message_id": 1, "Message": "Hello"}]
        mock_unread_count.return_value = 2

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/messages")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "inbox_page")
        mock_update_last_active.assert_called_once_with(5)
        mock_fetch_conversations.assert_called_once_with(5)
        mock_fetch_conversation.assert_called_once_with(5, 10)
        mock_mark_read.assert_called_once_with(5, 10)
        mock_render.assert_called_once()

    @patch("app.routes.messageroutes.MessageController.send_message")
    @patch("app.routes.messageroutes.MessageController.can_message")
    def test_send_message_success(self, mock_can_message, mock_send_message):
        mock_can_message.return_value = True
        mock_send_message.return_value = {"Message_id": 1}

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post("/messages/send", data={"receiver_id": 10, "message": "Hello"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "success", "message": "Message sent."})
        mock_can_message.assert_called_once_with(5, 10)
        mock_send_message.assert_called_once_with(5, 10, "Hello")

    def test_send_message_empty_message_validation(self):
        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post("/messages/send", data={"receiver_id": 10, "message": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"status": "error", "message": "Receiver and message are required."})

    @patch("app.routes.messageroutes.MessageController.can_message")
    def test_send_message_invalid_recipient(self, mock_can_message):
        mock_can_message.return_value = False

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post("/messages/send", data={"receiver_id": 10, "message": "Hello"})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {"status": "error", "message": "Invalid chat partner."})
        mock_can_message.assert_called_once_with(5, 10)

    @patch("app.routes.messageroutes.MessageController.can_message")
    @patch("app.routes.messageroutes.render_template")
    @patch("app.routes.messageroutes.MessageController.unread_count")
    @patch("app.routes.messageroutes.MessageController.mark_read")
    @patch("app.routes.messageroutes.MessageController.fetch_conversation")
    @patch("app.routes.messageroutes.UserModel.get_online_status")
    @patch("app.routes.messageroutes.UserModel.get_by_id")
    @patch("app.routes.messageroutes.MessageController.fetch_conversations")
    @patch("app.routes.messageroutes.UserModel.update_last_active")
    @patch("app.database.get_connection")
    def test_message_retrieval(
        self,
        mock_get_connection,
        mock_update_last_active,
        mock_fetch_conversations,
        mock_get_by_id,
        mock_get_online_status,
        mock_fetch_conversation,
        mock_mark_read,
        mock_unread_count,
        mock_render,
        mock_can_message,
    ):
        mock_render.return_value = "conversation_page"
        mock_fetch_conversations.return_value = []
        mock_get_by_id.return_value = {"User_id": 10, "First_name": "Alice", "Role": "employer"}
        mock_get_online_status.return_value = {"online": False}
        mock_fetch_conversation.return_value = [{"Message_id": 2, "Message": "Hi"}]
        mock_unread_count.return_value = 1
        mock_can_message.return_value = True
        mock_get_connection.return_value = MagicMock()

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/messages/10")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "conversation_page")
        mock_fetch_conversation.assert_called_once_with(5, 10)
        mock_mark_read.assert_called_once_with(5, 10)

    def test_redirect_behavior_for_unauthenticated_user(self):
        with self.app.test_client() as client:
            response = client.get("/messages")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    @patch("app.routes.messageroutes.MessageController.can_message")
    def test_redirect_behavior_for_invalid_conversation(self, mock_can_message):
        mock_can_message.return_value = False

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/messages/10")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/messages", response.location)


class TestMessageControllerLogic(unittest.TestCase):
    @patch("app.controllers.message_controller.NotificationController.create_notification")
    @patch("app.controllers.message_controller.UserModel.get_by_id")
    @patch("app.controllers.message_controller.UserModel.update_last_active")
    @patch("app.controllers.message_controller.MessageModel.send_message")
    @patch("app.controllers.message_controller.MessageController.can_message")
    def test_send_message_success(self, mock_can_message, mock_send_message, mock_update_last_active, mock_get_by_id, mock_create_notification):
        mock_can_message.return_value = True
        mock_send_message.return_value = {"Message_id": 1}
        mock_get_by_id.side_effect = [
            {"User_id": 10, "First_name": "Alice", "Last_name": "Smith", "Role": "employer"},
            {"User_id": 5, "First_name": "Bob", "Last_name": "Jones", "Role": "job_seeker"},
        ]

        result = MessageController.send_message(5, 10, "Hello")

        self.assertEqual(result, {"Message_id": 1})
        mock_update_last_active.assert_called_once_with(5)
        mock_send_message.assert_called_once_with(5, 10, "Hello")
        mock_create_notification.assert_called_once()

    @patch("app.controllers.message_controller.MessageModel.send_message")
    @patch("app.controllers.message_controller.MessageController.can_message")
    def test_send_message_empty_message_validation(self, mock_can_message, mock_send_message):
        mock_can_message.return_value = True
        mock_send_message.return_value = None

        result = MessageController.send_message(5, 10, "   ")

        self.assertIsNone(result)
        mock_send_message.assert_called_once_with(5, 10, "   ")

    @patch("app.controllers.message_controller.MessageController.can_message")
    def test_send_message_invalid_recipient(self, mock_can_message):
        mock_can_message.return_value = False

        result = MessageController.send_message(5, 5, "Hello")

        self.assertIsNone(result)
        mock_can_message.assert_called_once_with(5, 5)

    @patch("app.controllers.message_controller.MessageModel.get_by_id")
    def test_get_message_returns_message(self, mock_get_by_id):
        mock_get_by_id.return_value = {"Message_id": 1, "Message": "Hello"}

        result = MessageController.get_message(1)

        self.assertEqual(result, {"Message_id": 1, "Message": "Hello"})
        mock_get_by_id.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()

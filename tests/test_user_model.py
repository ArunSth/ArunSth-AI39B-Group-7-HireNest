import unittest
from unittest.mock import patch, MagicMock

from app.modals.user import UserModel


class TestUserModel(unittest.TestCase):
    @patch("app.modals.user.get_connection")
    def test_get_by_email_returns_matching_user(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "User_id": 42,
            "Email": "employer@example.com",
            "Role": "employer",
        }
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        result = UserModel.get_by_email("employer@example.com")

        self.assertEqual(result["User_id"], 42)
        mock_cursor.execute.assert_called_once()
        self.assertIn("WHERE `Email`=%s", mock_cursor.execute.call_args[0][0])
        self.assertEqual(
            mock_cursor.execute.call_args[0][1], ("employer@example.com",))


if __name__ == "__main__":
    unittest.main()

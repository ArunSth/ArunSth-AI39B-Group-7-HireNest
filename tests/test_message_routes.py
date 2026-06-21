import unittest
from unittest.mock import patch

from app import create_app


class TestMessageRouteTemplates(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True, SECRET_KEY='test-secret')
        self.client = self.app.test_client()

    @patch('app.routes.messageroutes.MessageController.mark_read')
    @patch('app.routes.messageroutes.MessageController.fetch_conversation')
    @patch('app.routes.messageroutes.MessageController.fetch_conversations')
    @patch('app.routes.messageroutes.MessageController.unread_count')
    @patch('app.routes.messageroutes.UserModel.get_online_status')
    @patch('app.routes.messageroutes.UserModel.get_by_id')
    @patch('app.routes.messageroutes.UserModel.update_last_active')
    def test_employer_messages_render_employer_template(
        self,
        mock_update_last_active,
        mock_get_by_id,
        mock_get_online_status,
        mock_unread_count,
        mock_fetch_conversations,
        mock_fetch_conversation,
        mock_mark_read,
    ):
        mock_get_by_id.return_value = {
            'User_id': 2,
            'Role': 'job_seeker',
            'First_name': 'Jane',
            'Last_name': 'Doe'
        }
        mock_get_online_status.return_value = {'online': False}
        mock_unread_count.return_value = 0
        mock_fetch_conversations.return_value = [
            {
                'user': {
                    'User_id': 2,
                    'First_name': 'Jane',
                    'Last_name': 'Doe',
                    'Role': 'job_seeker',
                    'Company_name': None
                },
                'last_message': {
                    'Created_at': '2024-01-01 10:00:00',
                    'Message': 'Hi there'
                },
                'unread_count': 0
            }
        ]
        mock_fetch_conversation.return_value = []

        with self.client.session_transaction() as session:
            session['user_id'] = 1
            session['role'] = 'employer'

        response = self.client.get('/messages')

        self.assertEqual(response.status_code, 200)
        self.assertIn('My Profile', response.data.decode())
        self.assertIn(
            'Manage conversations with candidates and job seekers.', response.data.decode())


if __name__ == '__main__':
    unittest.main()

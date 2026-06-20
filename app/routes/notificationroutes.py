from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.controllers.message_controller import MessageController
from app.controllers.notification_controller import NotificationController


class NotificationRoutes:
    def __init__(self):
        self.blueprint = Blueprint('notifications', __name__)

    def notifications(self):
        @self.blueprint.route('/notifications', methods=['GET'])
        def index():
            if 'user_id' not in session:
                return redirect(url_for('login.index'))

            user_id = session['user_id']
            notifications = NotificationController.fetch_notifications(user_id)
            return render_template(
                'notifications.html',
                notifications=notifications,
                unread_count=NotificationController.unread_count(user_id),
            )

        @self.blueprint.route('/notifications/recent', methods=['GET'])
        def recent():
            if 'user_id' not in session:
                return jsonify({'notifications': [], 'unread_count': 0}), 401

            user_id = session['user_id']
            notifications = NotificationController.fetch_recent_notifications(user_id)
            serialized = [
                {
                    'Notification_id': item['Notification_id'],
                    'Title': item.get('Title', 'Notification'),
                    'Message': item.get('Message', ''),
                    'Type': item.get('Type'),
                    'Reference_id': item.get('Reference_id'),
                    'Is_read': bool(item.get('Is_read', False)),
                    'Created_at': item.get('Created_at').strftime('%Y-%m-%d %H:%M:%S') if item.get('Created_at') else '',
                }
                for item in notifications
            ]
            return jsonify({
                'notifications': serialized,
                'unread_count': NotificationController.unread_count(user_id),
            })

        @self.blueprint.route('/notifications/read/<int:notification_id>', methods=['POST'])
        def mark_read(notification_id):
            if 'user_id' not in session:
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            updated = NotificationController.mark_read(
                notification_id, session['user_id'])
            return jsonify({'status': 'success' if updated else 'error', 'updated': updated})

        @self.blueprint.route('/notifications/open/<int:notification_id>', methods=['GET'])
        def open_notification(notification_id):
            if 'user_id' not in session:
                return redirect(url_for('login.index'))

            user_id = session['user_id']
            notification = NotificationController.get_notification(
                notification_id, user_id)
            if not notification:
                return redirect(url_for('notifications.index'))

            NotificationController.mark_read(notification_id, user_id)

            if notification.get('Type') == 'new_message' and notification.get('Reference_id'):
                message = MessageController.get_message(
                    notification['Reference_id'])
                if notification.get('Type') in ('job_deleted', 'job_rejected'):
                    return redirect(url_for('employer.dashboard'))
                if message and (message['Sender_id'] == user_id or message['Receiver_id'] == user_id):
                    other_user_id = message['Receiver_id'] if message['Sender_id'] == user_id else message['Sender_id']
                    return redirect(url_for('messages.conversation', conversation_id=other_user_id))

            return redirect(url_for('notifications.index'))

        @self.blueprint.route('/notifications/read-all', methods=['POST'])
        def mark_all_read():
            if 'user_id' not in session:
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            updated = NotificationController.mark_all_read(session['user_id'])
            return jsonify({'status': 'success' if updated or updated == 0 else 'error', 'updated': updated})

        @self.blueprint.route('/notifications/unread-count', methods=['GET'])
        def unread_count():
            if 'user_id' not in session:
                return jsonify({'count': 0}), 401

            return jsonify({'count': NotificationController.unread_count(session['user_id'])})

        return self.blueprint

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

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

        @self.blueprint.route('/notifications/read/<int:notification_id>', methods=['POST'])
        def mark_read(notification_id):
            if 'user_id' not in session:
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            updated = NotificationController.mark_read(
                notification_id, session['user_id'])
            return jsonify({'status': 'success' if updated else 'error', 'updated': updated})

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

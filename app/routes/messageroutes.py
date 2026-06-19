from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.controllers.message_controller import MessageController
from app.modals.user import UserModel


class MessageRoutes:
    def __init__(self):
        self.blueprint = Blueprint('messages', __name__)

    def messages(self):
        @self.blueprint.route('/messages', methods=['GET'])
        def index():
            if 'user_id' not in session:
                return redirect(url_for('login.index'))

            user_id = session['user_id']
            conversations = MessageController.fetch_conversations(user_id)
            selected_user = None
            messages = []

            if conversations:
                selected_user = conversations[0]['user']
                messages = MessageController.fetch_conversation(
                    user_id, selected_user['User_id'])
                MessageController.mark_read(user_id, selected_user['User_id'])

            return render_template(
                'messages.html',
                conversations=conversations,
                selected_user=selected_user,
                messages=messages,
                unread_count=MessageController.unread_count(user_id),
            )

        @self.blueprint.route('/messages/<int:conversation_id>', methods=['GET'])
        def conversation(conversation_id):
            if 'user_id' not in session:
                return redirect(url_for('login.index'))

            user_id = session['user_id']
            if not MessageController.can_message(user_id, conversation_id):
                return redirect(url_for('messages.index'))

            conversations = MessageController.fetch_conversations(user_id)
            selected_user = UserModel.get_by_id(conversation_id)
            messages = MessageController.fetch_conversation(
                user_id, conversation_id)
            MessageController.mark_read(user_id, conversation_id)

            return render_template(
                'messages.html',
                conversations=conversations,
                selected_user=selected_user,
                messages=messages,
                unread_count=MessageController.unread_count(user_id),
            )

        @self.blueprint.route('/messages/send', methods=['POST'])
        def send_message():
            if 'user_id' not in session:
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            sender_id = session['user_id']
            receiver_id = request.form.get('receiver_id', type=int)
            content = request.form.get('message', '').strip()

            if not receiver_id or not content:
                return jsonify({'status': 'error', 'message': 'Receiver and message are required.'}), 400

            message = MessageController.send_message(
                sender_id, receiver_id, content)
            if message:
                return jsonify({'status': 'success', 'message': 'Message sent.', 'data': message}), 200
            return jsonify({'status': 'error', 'message': 'Message could not be sent.'}), 400

        @self.blueprint.route('/messages/unread-count', methods=['GET'])
        def unread_count():
            if 'user_id' not in session:
                return jsonify({'count': 0}), 401

            return jsonify({'count': MessageController.unread_count(session['user_id'])})

        return self.blueprint

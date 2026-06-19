from app.modals.message import MessageModel
from app.modals.user import UserModel
from app.controllers.notification_controller import NotificationController


class MessageController:
    @staticmethod
    def fetch_conversations(user_id):
        return MessageModel.get_conversations(user_id)

    @staticmethod
    def fetch_conversation(user_id, conversation_id):
        return MessageModel.get_conversation(user_id, conversation_id)

    @staticmethod
    def send_message(sender_id, receiver_id, content):
        if not MessageController.can_message(sender_id, receiver_id):
            return None
        UserModel.update_last_active(sender_id)
        message = MessageModel.send_message(sender_id, receiver_id, content)
        if message:
            receiver = UserModel.get_by_id(receiver_id)
            sender = UserModel.get_by_id(sender_id)
            if receiver:
                NotificationController.create_notification(
                    receiver_id,
                    'New message',
                    f"New message from {sender.get('First_name', '')} {sender.get('Last_name', '')}",
                    'new_message',
                    message.get('Message_id'),
                )
        return message

    @staticmethod
    def mark_message_seen(message_id, receiver_id):
        return MessageModel.mark_message_seen(message_id, receiver_id)

    @staticmethod
    def get_message(message_id):
        return MessageModel.get_by_id(message_id)

    @staticmethod
    def can_message(user_id, conversation_id):
        if not user_id or not conversation_id or user_id == conversation_id:
            return False

        current_user = UserModel.get_by_id(user_id)
        other_user = UserModel.get_by_id(conversation_id)
        if not current_user or not other_user:
            return False

        valid_roles = {'job_seeker', 'employer'}
        if current_user.get('Role') not in valid_roles or other_user.get('Role') not in valid_roles:
            return False

        return current_user.get('Role') != other_user.get('Role')

    @staticmethod
    def mark_read(user_id, sender_id):
        return MessageModel.mark_messages_read(user_id, sender_id)

    @staticmethod
    def unread_count(user_id):
        return MessageModel.unread_count(user_id)
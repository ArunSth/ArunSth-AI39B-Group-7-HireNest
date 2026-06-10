from app.modals.message import MessageModel
from app.modals.notification import NotificationModel
from app.modals.user import UserModel


class MessageController:
    @staticmethod
    def fetch_conversations(user_id):
        return MessageModel.get_conversations(user_id)

    @staticmethod
    def fetch_conversation(user_id, conversation_id):
        return MessageModel.get_conversation(user_id, conversation_id)

    @staticmethod
    def send_message(sender_id, receiver_id, content):
        message = MessageModel.send_message(sender_id, receiver_id, content)
        if message:
            sender = UserModel.get_by_id(sender_id)
            sender_name = f"{sender.get('First_name', '')} {sender.get('Last_name', '')}".strip(
            ) if sender else 'Someone'
            NotificationModel.create_notification(
                receiver_id,
                'New message',
                f"{sender_name} sent you a message.",
                'new_message',
                message['Message_id'],
            )
        return message

    @staticmethod
    def mark_read(user_id, sender_id):
        return MessageModel.mark_messages_read(user_id, sender_id)

    @staticmethod
    def unread_count(user_id):
        return MessageModel.unread_count(user_id)

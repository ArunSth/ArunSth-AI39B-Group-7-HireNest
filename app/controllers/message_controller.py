from app.modals.message import MessageModel


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
        return message

    @staticmethod
    def mark_read(user_id, sender_id):
        return MessageModel.mark_messages_read(user_id, sender_id)

    @staticmethod
    def unread_count(user_id):
        return MessageModel.unread_count(user_id)
from app.modals.notification import NotificationModel


class NotificationController:
    @staticmethod
    def create_notification(user_id, title, message, notification_type='general', reference_id=None):
        return NotificationModel.create_notification(user_id, title, message, notification_type, reference_id)

    @staticmethod
    def fetch_notifications(user_id):
        return NotificationModel.get_notifications(user_id)

    @staticmethod
    def unread_count(user_id):
        return NotificationModel.unread_count(user_id)

    @staticmethod
    def mark_read(notification_id, user_id):
        return NotificationModel.mark_read(notification_id, user_id)

    @staticmethod
    def mark_all_read(user_id):
        return NotificationModel.mark_all_read(user_id)

from app.database import get_connection


class NotificationModel:
    @staticmethod
    def create_notification(user_id, title, message, notification_type='general', reference_id=None):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Notification` (`User_id`, `Title`, `Message`, `Type`, `Reference_id`, `Is_read`, `Created_at`)
                    VALUES (%s, %s, %s, %s, %s, FALSE, NOW())
                    """,
                    (user_id, title, message, notification_type, reference_id),
                )
                conn.commit()
                cur.execute("SELECT LAST_INSERT_ID() AS notification_id")
                return cur.fetchone()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_notifications(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM `Notification`
                    WHERE `User_id` = %s
                    ORDER BY `Notification_id` DESC
                    """,
                    (user_id,),
                )
                return cur.fetchall() or []
        finally:
            conn.close()

    @staticmethod
    def get_notification(notification_id, user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM `Notification`
                    WHERE `Notification_id` = %s
                      AND `User_id` = %s
                    """,
                    (notification_id, user_id),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def send_announcement(subject, message, audience, db=None):
        """
        audience: 'all' | 'Job Seeker' | 'Employer'
        db: retained for backward compatibility; not required by the current model layer.
        """
        from app.modals.user import UserModel
        from app.modals.notification import NotificationModel

        all_users = UserModel.get_all_users()
        if audience == 'all':
            users = all_users
        else:
            role_map = {
                'Job Seeker': 'job_seeker',
                'Employer': 'employer',
            }
            normalized_role = role_map.get(audience, audience)
            users = [user for user in all_users if user.get(
                'Role') == normalized_role]

        for user in users:
            NotificationModel.create_notification(
                user_id=user['User_id'],
                title=f"📢 {subject}",
                message=message,
                notification_type='general',
            )

        return len(users)

    @staticmethod
    def unread_count(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) AS cnt
                    FROM `Notification`
                    WHERE `User_id` = %s
                      AND (`Is_read` IS NULL OR `Is_read` = FALSE)
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
                return int(row['cnt']) if row else 0
        finally:
            conn.close()

    @staticmethod
    def mark_read(notification_id, user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Notification`
                    SET `Is_read` = TRUE
                    WHERE `Notification_id` = %s
                      AND `User_id` = %s
                    """,
                    (notification_id, user_id),
                )
                conn.commit()
                return cur.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def mark_all_read(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Notification`
                    SET `Is_read` = TRUE
                    WHERE `User_id` = %s
                    """,
                    (user_id,),
                )
                conn.commit()
                return cur.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

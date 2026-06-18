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
    def send_announcement(subject, message, audience, db):
        """
        audience: 'all' | 'Job Seeker' | 'Employer'
        db: your SQLAlchemy db instance (or however you access the session)
 
        Adjust the import / query style to match your existing controller patterns.
        """
        from app.models.user import User            # adjust import path as needed
        from app.models.notification import Notification  # adjust import path as needed
 
    # Build the recipient query
        if audience == 'all':
           users = db.session.query(User).all()
        else:
           users = db.session.query(User).filter(User.Role == audience).all()
 
        notifications = [
            Notification(
              user_id=u.User_id,
              title=f"📢 {subject}",
              message=message,
              is_read=False,
            )
            for u in users
        ]
 
        if notifications:
            db.session.bulk_save_objects(notifications)
            db.session.commit()
 
        return len(notifications)
 

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

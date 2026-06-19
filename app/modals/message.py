from app.database import get_connection


class MessageModel:
    @staticmethod
    def get_conversations(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT m.*, sender.First_name AS sender_first_name,
                           sender.Last_name AS sender_last_name,
                           sender.Email AS sender_email,
                           sender.Role AS sender_role,
                           sender.Last_active_at AS sender_last_active_at,
                           receiver.First_name AS receiver_first_name,
                           receiver.Last_name AS receiver_last_name,
                           receiver.Email AS receiver_email,
                           receiver.Role AS receiver_role,
                           receiver.Last_active_at AS receiver_last_active_at,
                           sender_emp.Company_name AS sender_company_name,
                           receiver_emp.Company_name AS receiver_company_name
                    FROM `Messages` m
                    JOIN `User` sender ON sender.User_id = m.Sender_id
                    JOIN `User` receiver ON receiver.User_id = m.Receiver_id
                    LEFT JOIN `Employee` sender_emp ON sender_emp.User_id = sender.User_id
                    LEFT JOIN `Employee` receiver_emp ON receiver_emp.User_id = receiver.User_id
                    WHERE (m.Sender_id = %s OR m.Receiver_id = %s)
                    ORDER BY m.Created_at DESC, m.Message_id DESC
                    """,
                    (user_id, user_id),
                )
                rows = cur.fetchall() or []

            conversations = {}
            for row in rows:
                other_user_id = row['Receiver_id'] if row['Sender_id'] == user_id else row['Sender_id']
                other_user = {
                    'User_id': other_user_id,
                    'First_name': row['receiver_first_name'] if row['Sender_id'] == user_id else row['sender_first_name'],
                    'Last_name': row['receiver_last_name'] if row['Sender_id'] == user_id else row['sender_last_name'],
                    'Email': row['receiver_email'] if row['Sender_id'] == user_id else row['sender_email'],
                    'Role': row['receiver_role'] if row['Sender_id'] == user_id else row['sender_role'],
                    'Last_active_at': row['receiver_last_active_at'] if row['Sender_id'] == user_id else row['sender_last_active_at'],
                    'Company_name': row['receiver_company_name'] if row['Sender_id'] == user_id else row['sender_company_name'],
                }

                if other_user_id not in conversations:
                    conversations[other_user_id] = {
                        'user': other_user,
                        'last_message': row,
                        'unread_count': 0,
                        'last_activity': row.get('Created_at'),
                    }

                if row.get('Created_at') and (
                    not conversations[other_user_id]['last_activity'] or row['Created_at'] > conversations[other_user_id]['last_activity']
                ):
                    conversations[other_user_id]['last_message'] = row
                    conversations[other_user_id]['last_activity'] = row['Created_at']

                if row['Receiver_id'] == user_id and not row.get('Is_read', False):
                    conversations[other_user_id]['unread_count'] += 1

            return sorted(
                conversations.values(),
                key=lambda item: item['last_activity'] or item['last_message'].get(
                    'Created_at') or '',
                reverse=True,
            )
        finally:
            conn.close()

    @staticmethod
    def get_conversation(user_id, other_user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT m.*, sender.First_name AS sender_first_name, sender.Last_name AS sender_last_name
                    FROM `Messages` m
                    JOIN `User` sender ON sender.User_id = m.Sender_id
                    WHERE ((m.Sender_id = %s AND m.Receiver_id = %s) OR (m.Sender_id = %s AND m.Receiver_id = %s))
                    ORDER BY m.Created_at ASC, m.Message_id ASC
                    """,
                    (user_id, other_user_id, other_user_id, user_id),
                )
                return cur.fetchall() or []
        finally:
            conn.close()

    @staticmethod
    def mark_message_seen(message_id, receiver_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Messages`
                    SET `Is_read` = TRUE, `Status` = 'seen'
                    WHERE `Message_id` = %s
                      AND `Receiver_id` = %s
                      AND (`Is_read` IS NULL OR `Is_read` = FALSE)
                    """,
                    (message_id, receiver_id),
                )
                conn.commit()
                return cur.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_by_id(message_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Messages` WHERE `Message_id`=%s",
                    (message_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def send_message(sender_id, receiver_id, message_text):
        if not message_text.strip():
            return None

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Messages` (`Sender_id`, `Receiver_id`, `Message`, `Is_read`, `Created_at`, `Status`)
                    VALUES (%s, %s, %s, FALSE, NOW(), 'sent')
                    """,
                    (sender_id, receiver_id, message_text.strip()),
                )
                conn.commit()
                cur.execute("SELECT LAST_INSERT_ID() AS message_id")
                message_id = cur.fetchone()['message_id']
                cur.execute(
                    "SELECT * FROM `Messages` WHERE `Message_id`=%s", (message_id,))
                return cur.fetchone()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def mark_messages_read(user_id, sender_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Messages`
                    SET `Is_read` = TRUE,
                        `Status` = 'seen'
                    WHERE `Receiver_id` = %s
                      AND `Sender_id` = %s
                      AND (`Is_read` IS NULL OR `Is_read` = FALSE)
                    """,
                    (user_id, sender_id),
                )
                conn.commit()
                return cur.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def unread_count(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) AS cnt
                    FROM `Messages`
                    WHERE `Receiver_id` = %s
                      AND (`Is_read` IS NULL OR `Is_read` = FALSE)
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
                return int(row['cnt']) if row else 0
        finally:
            conn.close()

    @staticmethod
    def get_message(message_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Messages` WHERE `Message_id`=%s",
                    (message_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

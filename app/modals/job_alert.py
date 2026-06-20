from app.database import get_connection


class JobAlertModel:
    @staticmethod
    def create_alert(seeker_id, keyword, location, frequency, job_type=None, industry=None, is_active=True):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Job_Alerts` (`Seekers_id`, `Keyword`, `Location`, `Frequency`, `Job_type`, `Industry`, `Is_active`, `Created_at`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (seeker_id, keyword, location, frequency,
                     job_type, industry, is_active),
                )
                conn.commit()
                cur.execute("SELECT LAST_INSERT_ID() AS alert_id")
                return cur.fetchone()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_alerts(seeker_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM `Job_Alerts`
                    WHERE `Seekers_id` = %s
                    ORDER BY `Alert_id` DESC
                    """,
                    (seeker_id,),
                )
                return cur.fetchall() or []
        finally:
            conn.close()

    @staticmethod
    def get_alert(alert_id, seeker_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM `Job_Alerts`
                    WHERE `Alert_id` = %s AND `Seekers_id` = %s
                    """,
                    (alert_id, seeker_id),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update_alert(alert_id, seeker_id, keyword, location, frequency, job_type=None, industry=None, is_active=True):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Job_Alerts`
                    SET `Keyword`=%s,
                        `Location`=%s,
                        `Frequency`=%s,
                        `Job_type`=%s,
                        `Industry`=%s,
                        `Is_active`=%s
                    WHERE `Alert_id`=%s AND `Seekers_id`=%s
                    """,
                    (keyword, location, frequency, job_type,
                     industry, is_active, alert_id, seeker_id),
                )
                conn.commit()
                return cur.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def delete_alert(alert_id, seeker_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM `Job_Alerts`
                    WHERE `Alert_id` = %s AND `Seekers_id` = %s
                    """,
                    (alert_id, seeker_id),
                )
                conn.commit()
                return cur.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def find_matching_job_seekers_for_job(title, location, job_type=None, industry=None, description=None, requirement=None):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT DISTINCT u.`User_id`
                    FROM `Job_Alerts` a
                    JOIN `Job_Seekers` s ON a.`Seekers_id` = s.`Seekers_id`
                    JOIN `User` u ON s.`User_id` = u.`User_id`
                    WHERE a.`Is_active` = TRUE
                      AND (a.`Location` IS NULL OR a.`Location` = '' OR %s LIKE CONCAT('%', a.`Location`, '%'))
                      AND (a.`Job_type` IS NULL OR a.`Job_type` = '' OR a.`Job_type` = %s)
                      AND (a.`Industry` IS NULL OR a.`Industry` = '' OR a.`Industry` = %s)
                      AND (
                          a.`Keyword` IS NULL
                          OR a.`Keyword` = ''
                          OR LOWER(%s) LIKE CONCAT('%', LOWER(a.`Keyword`), '%')
                          OR LOWER(%s) LIKE CONCAT('%', LOWER(a.`Keyword`), '%')
                          OR LOWER(%s) LIKE CONCAT('%', LOWER(a.`Keyword`), '%')
                      )
                """
                params = [location or '', job_type or '', industry or '', title or '', description or '', requirement or '']
                cur.execute(query, params)
                return [row['User_id'] for row in cur.fetchall()]
        finally:
            conn.close()

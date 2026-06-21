from app.database import get_connection


class JobReportModel:
    @staticmethod
    def create_report(job_id, reporter_user_id, reason, details, status="Pending"):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Job_Reports`
                    (`Job_id`, `Reporter_user_id`, `Reason`, `Details`, `Status`, `Created_at`)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    """,
                    (job_id, reporter_user_id, reason, details, status),
                )
                conn.commit()
                return cur.lastrowid
        except Exception:
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def has_reported(job_id, reporter_user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM `Job_Reports`
                    WHERE `Job_id` = %s AND `Reporter_user_id` = %s
                    LIMIT 1
                    """,
                    (job_id, reporter_user_id),
                )
                return cur.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def get_reports_for_admin():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        jr.`Report_id`,
                        jr.`Job_id`,
                        jr.`Reporter_user_id`,
                        jr.`Reason`,
                        jr.`Details`,
                        jr.`Status`,
                        jr.`Created_at`,
                        jr.`Resolved_at`,
                        jr.`Resolved_by_user_id`,
                        j.`Title` AS `Job_title`,
                        e.`Company_name`,
                        u.`First_name` AS `Reporter_first_name`,
                        u.`Last_name` AS `Reporter_last_name`
                    FROM `Job_Reports` jr
                    JOIN `Jobs` j ON jr.`Job_id` = j.`Job_id`
                    JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    JOIN `User` u ON jr.`Reporter_user_id` = u.`User_id`
                    ORDER BY jr.`Created_at` DESC
                    """
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_report_by_id(report_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        jr.*,
                        j.`Title` AS `Job_title`,
                        e.`Company_name`,
                        u.`First_name` AS `Reporter_first_name`,
                        u.`Last_name` AS `Reporter_last_name`
                    FROM `Job_Reports` jr
                    JOIN `Jobs` j ON jr.`Job_id` = j.`Job_id`
                    JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    JOIN `User` u ON jr.`Reporter_user_id` = u.`User_id`
                    WHERE jr.`Report_id` = %s
                    """,
                    (report_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def mark_resolved(report_id, admin_user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Job_Reports`
                    SET `Status` = 'Resolved',
                        `Resolved_at` = NOW(),
                        `Resolved_by_user_id` = %s
                    WHERE `Report_id` = %s
                    """,
                    (admin_user_id, report_id),
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def mark_dismissed(report_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Job_Reports`
                    SET `Status` = 'Dismissed'
                    WHERE `Report_id` = %s
                    """,
                    (report_id,),
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

from app.database import get_connection


class SavedJobModel:
    @staticmethod
    def is_saved(seekers_id, job_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT `Saved_id`
                    FROM `Saved_Jobs`
                    WHERE `Seekers_id`=%s AND `Job_id`=%s
                    LIMIT 1
                    """,
                    (seekers_id, job_id),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def save_job(seekers_id, job_id):
        if SavedJobModel.is_saved(seekers_id, job_id):
            return True

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Saved_Jobs` (`Seekers_id`, `Job_id`)
                    VALUES (%s, %s)
                    """,
                    (seekers_id, job_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving job: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def unsave_job(seekers_id, job_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM `Saved_Jobs`
                    WHERE `Seekers_id`=%s AND `Job_id`=%s
                    """,
                    (seekers_id, job_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error unsaving job: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_saved_jobs(seekers_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        s.`Saved_id`,
                        j.`Job_id`,
                        j.`Title`,
                        j.`Description`,
                        j.`Requirement`,
                        j.`Salary`,
                        j.`Location`,
                        j.`Status`,
                        j.`Job_type`,
                        j.`Experience_level`,
                        j.`Created_at`,
                        e.`Employee_id`,
                        e.`Company_name`,
                        e.`Industry`,
                        e.`Logo`
                    FROM `Saved_Jobs` s
                    JOIN `Jobs` j ON s.`Job_id` = j.`Job_id`
                    JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    WHERE s.`Seekers_id`=%s
                    ORDER BY s.`Saved_id` DESC
                    """,
                    (seekers_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def count_saved_jobs(seekers_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM `Saved_Jobs` WHERE `Seekers_id`=%s",
                    (seekers_id,),
                )
                row = cur.fetchone()
                return row["total"] if row else 0
        finally:
            conn.close()

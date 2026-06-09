from app.database import get_connection
from datetime import datetime

class JobPostingModel:
    @staticmethod
    def create_job(employee_id, title, description, requirement, salary, location, job_type="Full-time", experience_level="Entry-level"):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Jobs` (`Employee_id`, `Title`, `Description`, `Requirement`, `Salary`, `Location`, `Status`, `Job_type`, `Experience_level`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (employee_id, title, description, requirement, salary, location, "active", job_type, experience_level),
                )
                conn.commit()
                job_id = cur.lastrowid
                return job_id
        except Exception as e:
            print(f"Error creating job: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_jobs_by_employer(employee_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT `Job_id`, `Title`, `Description`, `Requirement`, `Salary`, `Location`, `Status`, `Created_at`, `Job_type`, `Experience_level`
                    FROM `Jobs`
                    WHERE `Employee_id`=%s
                    ORDER BY `Created_at` DESC
                    """,
                    (employee_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_job_by_id(job_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM `Jobs`
                    WHERE `Job_id`=%s
                    """,
                    (job_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update_job(job_id, title, description, requirement, salary, location, job_type, experience_level):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Jobs`
                    SET `Title`=%s, `Description`=%s, `Requirement`=%s, `Salary`=%s, `Location`=%s, `Job_type`=%s, `Experience_level`=%s
                    WHERE `Job_id`=%s
                    """,
                    (title, description, requirement, salary, location, job_type, experience_level, job_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating job: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def delete_job(job_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM `Jobs` WHERE `Job_id`=%s", (job_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting job: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def update_job_status(job_id, status):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Jobs` SET `Status`=%s WHERE `Job_id`=%s",
                    (status, job_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating job status: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_application_count(job_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as count FROM `Applications` WHERE `Job_id`=%s",
                    (job_id,),
                )
                result = cur.fetchone()
                return result['count'] if result else 0
        finally:
            conn.close()

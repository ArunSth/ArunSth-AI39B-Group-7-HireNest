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
    def search_jobs(keyword, location, job_type):
        conn = get_connection()
        try:
            query = """
                SELECT j.*, e.`Company_name`, e.`Industry`, e.`Logo`
                FROM `Jobs` j
                JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                WHERE j.`Status` = 'active'
            """
            params = []
 
            if keyword:
                query += " AND (j.`Title` LIKE %s OR j.`Description` LIKE %s OR j.`Requirement` LIKE %s)"
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
 
            if location:
                query += " AND j.`Location` LIKE %s"
                params.append(f"%{location}%")
 
            if job_type and job_type != "All Types":
                query += " AND j.`Job_type` = %s"
                params.append(job_type)
 
            query += " ORDER BY j.`Created_at` DESC"
 
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def search_jobs_for_seekers(filters, seekers_id=None):
        conn = get_connection()
        try:
            query = """
                SELECT
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
            """
            params = []

            if seekers_id:
                query += """,
                    CASE WHEN sj.`Saved_id` IS NULL THEN 0 ELSE 1 END AS `Is_saved`,
                    CASE WHEN a.`Application_id` IS NULL THEN 0 ELSE 1 END AS `Has_applied`
                """
            else:
                query += ", 0 AS `Is_saved`, 0 AS `Has_applied`"

            query += """
                FROM `Jobs` j
                JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
            """

            if seekers_id:
                query += """
                    LEFT JOIN `Saved_Jobs` sj
                        ON sj.`Job_id` = j.`Job_id` AND sj.`Seekers_id` = %s
                    LEFT JOIN `Applications` a
                        ON a.`Job_id` = j.`Job_id` AND a.`Seekers_id` = %s
                """
                params.extend([seekers_id, seekers_id])

            query += " WHERE LOWER(j.`Status`) = 'active'"

            keyword = filters.get("keyword")
            if keyword:
                query += " AND (j.`Title` LIKE %s OR j.`Description` LIKE %s OR j.`Requirement` LIKE %s)"
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

            company = filters.get("company")
            if company:
                query += " AND e.`Company_name` LIKE %s"
                params.append(f"%{company}%")

            location = filters.get("location")
            if location:
                query += " AND j.`Location` LIKE %s"
                params.append(f"%{location}%")

            industry = filters.get("industry")
            if industry:
                query += " AND e.`Industry` LIKE %s"
                params.append(f"%{industry}%")

            job_type = filters.get("job_type")
            if job_type and job_type != "All Types":
                query += " AND j.`Job_type` = %s"
                params.append(job_type)

            experience_level = filters.get("experience_level")
            if experience_level and experience_level != "All Levels":
                query += " AND j.`Experience_level` = %s"
                params.append(experience_level)

            salary_min = filters.get("salary_min")
            if salary_min:
                query += " AND j.`Salary` >= %s"
                params.append(salary_min)

            salary_max = filters.get("salary_max")
            if salary_max:
                query += " AND j.`Salary` <= %s"
                params.append(salary_max)

            query += " ORDER BY j.`Created_at` DESC"

            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Error searching seeker jobs: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_job_detail_for_seeker(job_id, seekers_id=None):
        conn = get_connection()
        try:
            query = """
                SELECT
                    j.*,
                    e.`Employee_id`,
                    e.`Company_name`,
                    e.`Industry`,
                    e.`Logo`,
                    e.`Website`,
                    e.`Description` AS `Company_description`
            """
            params = []

            if seekers_id:
                query += """,
                    CASE WHEN sj.`Saved_id` IS NULL THEN 0 ELSE 1 END AS `Is_saved`,
                    CASE WHEN a.`Application_id` IS NULL THEN 0 ELSE 1 END AS `Has_applied`
                """
            else:
                query += ", 0 AS `Is_saved`, 0 AS `Has_applied`"

            query += """
                FROM `Jobs` j
                JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
            """

            if seekers_id:
                query += """
                    LEFT JOIN `Saved_Jobs` sj
                        ON sj.`Job_id` = j.`Job_id` AND sj.`Seekers_id` = %s
                    LEFT JOIN `Applications` a
                        ON a.`Job_id` = j.`Job_id` AND a.`Seekers_id` = %s
                """
                params.extend([seekers_id, seekers_id])

            query += " WHERE j.`Job_id`=%s"
            params.append(job_id)

            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()
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
                    SELECT j.*, e.`Company_name`, e.`Industry`, e.`Website`, e.`Logo`
                    FROM `Jobs` j
                    JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    WHERE j.`Job_id`=%s
                    """,
                    (job_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_saved_jobs(seekers_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT j.*, e.`Company_name`, e.`Industry`, s.`Saved_id`
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
    def get_saved_job_ids(seekers_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT `Job_id` FROM `Saved_Jobs` WHERE `Seekers_id`=%s", (seekers_id,))
                return {row["Job_id"] for row in cur.fetchall()}
        finally:
            conn.close()

    @staticmethod
    def save_job(seekers_id, job_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT `Saved_id` FROM `Saved_Jobs` WHERE `Seekers_id`=%s AND `Job_id`=%s",
                    (seekers_id, job_id),
                )
                if cur.fetchone():
                    return True
                cur.execute(
                    "INSERT INTO `Saved_Jobs` (`Seekers_id`, `Job_id`) VALUES (%s, %s)",
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
                    "DELETE FROM `Saved_Jobs` WHERE `Seekers_id`=%s AND `Job_id`=%s",
                    (seekers_id, job_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error removing saved job: {e}")
            conn.rollback()
            return False
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
    def get_active_jobs():
        """Returns count of all active jobs."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # FIX: was `Job` (wrong), correct table name is `Jobs`
                cur.execute("SELECT COUNT(*) as total FROM `Jobs` WHERE `Status` = 'active'")
                result = cur.fetchone()
                return result['total'] if result else 0
        except Exception as e:
            print(f"Error getting active jobs count: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_all_jobs_for_admin():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT j.`Job_id`, j.`Title`, j.`Description`, j.`Location`,
                           j.`Job_type`, j.`Status`, j.`Created_at`,
                           COALESCE(e.`Company_name`, 'Unknown') AS `Company_name`
                    FROM `Jobs` j
                    JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    ORDER BY j.`Created_at` DESC
                    """
                )
                return cur.fetchall()
        except Exception as ex:
            print(f"Error fetching jobs for admin: {ex}")
            return []
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
        except Exception as e:
            print(f"Error getting application count: {e}")
            return 0
        finally:
            conn.close()
 
    @staticmethod
    def get_total_jobs():
        """Returns total count of all jobs regardless of status."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as total FROM `Jobs`")
                result = cur.fetchone()
                return result['total'] if result else 0
        except Exception as e:
            print(f"Error getting total jobs count: {e}")
            return 0
        finally:
            conn.close()

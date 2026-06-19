from app.database import get_connection

class ApplicantManagementModel:
    @staticmethod
    def has_applied(seekers_id, job_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT `Application_id`
                    FROM `Applications`
                    WHERE `Seekers_id`=%s AND `Job_id`=%s
                    LIMIT 1
                    """,
                    (seekers_id, job_id),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def create_application(seekers_id, job_id, resume, cover_letter, status="Pending"):
        if ApplicantManagementModel.has_applied(seekers_id, job_id):
            return None

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Applications`
                        (`Seekers_id`, `Job_id`, `Resume`, `Cover_letter`, `Status`)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (seekers_id, job_id, resume, cover_letter, status),
                )
                conn.commit()
                return cur.lastrowid
        except Exception as e:
            print(f"Error creating application: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_applications_for_employer(employee_id):
        """Get all applications for jobs posted by employer"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        a.`Application_id`, 
                        a.`Seekers_id`, 
                        a.`Job_id`, 
                        a.`Status`,
                        a.`Applied_at`,
                        a.`Cover_letter`,
                        j.`Title` as job_title,
                        js.`User_id` as job_seeker_user_id,
                        u.`First_name`,
                        u.`Last_name`,
                        u.`Email`
                    FROM `Applications` a
                    JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                    JOIN `Job_Seekers` js ON a.`Seekers_id` = js.`Seekers_id`
                    JOIN `User` u ON js.`User_id` = u.`User_id`
                    WHERE j.`Employee_id`=%s
                    ORDER BY a.`Applied_at` DESC
                    """,
                    (employee_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_applications_for_job(job_id):
        """Get all applications for a specific job"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        a.`Application_id`, 
                        a.`Seekers_id`, 
                        a.`Status`,
                        a.`Applied_at`,
                        a.`Cover_letter`,
                        js.`User_id` as job_seeker_user_id,
                        u.`First_name`,
                        u.`Last_name`,
                        u.`Email`
                    FROM `Applications` a
                    JOIN `Job_Seekers` js ON a.`Seekers_id` = js.`Seekers_id`
                    JOIN `User` u ON js.`User_id` = u.`User_id`
                    WHERE a.`Job_id`=%s
                    ORDER BY a.`Applied_at` DESC
                    """,
                    (job_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_application_details(application_id):
        """Get detailed information about an application"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        a.`Application_id`, 
                        a.`Seekers_id`, 
                        a.`Job_id`, 
                        a.`Status`,
                        a.`Applied_at`,
                        a.`Cover_letter`,
                        a.`Resume`,
                        j.`Title` as job_title,
                        j.`Salary`,
                        js.`User_id` as job_seeker_user_id,
                        js.`Bio`,
                        js.`Location`,
                        js.`Education`,
                        js.`Skills`,
                        js.`Experiences`,
                        js.`Resume` as seeker_resume,
                        u.`First_name`,
                        u.`Last_name`,
                        u.`Email`
                    FROM `Applications` a
                    JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                    JOIN `Job_Seekers` js ON a.`Seekers_id` = js.`Seekers_id`
                    JOIN `User` u ON js.`User_id` = u.`User_id`
                    WHERE a.`Application_id`=%s
                    """,
                    (application_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update_application_status(application_id, status):
        """Update application status (accepted, rejected, shortlisted, etc.)"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Applications` SET `Status`=%s WHERE `Application_id`=%s",
                    (status, application_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating application status: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_application_by_id(application_id):
        """Get a single application record"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Applications` WHERE `Application_id`=%s",
                    (application_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_status_count(employee_id):
        """Get count of applications by status for employer"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        a.`Status`, 
                        COUNT(a.`Application_id`) as count
                    FROM `Applications` a
                    JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                    WHERE j.`Employee_id`=%s
                    GROUP BY a.`Status`
                    """,
                    (employee_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_total_applicants(employee_id):
        """Get total applicants count for employer"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(DISTINCT a.`Application_id`) as count
                    FROM `Applications` a
                    JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                    WHERE j.`Employee_id`=%s
                    """,
                    (employee_id,),
                )
                result = cur.fetchone()
                return result['count'] if result else 0
        finally:
            conn.close()

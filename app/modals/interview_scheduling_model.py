from app.database import get_connection
from datetime import datetime

class InterviewSchedulingModel:
    @staticmethod
    def schedule_interview(application_id, interview_date, interview_time, meeting_link, mode="Google Meet", status="scheduled"):
        """Schedule an interview for an application"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Interview` (`Application_id`, `Interview_date`, `Interview_time`, `Meeting_link`, `Mode`, `Status`)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (application_id, interview_date, interview_time, meeting_link, mode, status),
                )
                conn.commit()
                interview_id = cur.lastrowid
                return interview_id
        except Exception as e:
            print(f"Error scheduling interview: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_interviews_for_employer(employee_id):
        """Get all interviews for employer's job postings"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        i.`Interview_id`, 
                        i.`Application_id`, 
                        i.`Interview_date`, 
                        i.`Interview_time`, 
                        i.`Meeting_link`, 
                        i.`Mode`, 
                        i.`Status`,
                        a.`Seekers_id`,
                        a.`Job_id`,
                        j.`Title` as job_title,
                        u.`First_name`,
                        u.`Last_name`,
                        u.`Email`
                    FROM `Interview` i
                    JOIN `Applications` a ON i.`Application_id` = a.`Application_id`
                    JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                    JOIN `Job_Seekers` js ON a.`Seekers_id` = js.`Seekers_id`
                    JOIN `User` u ON js.`User_id` = u.`User_id`
                    WHERE j.`Employee_id`=%s
                    ORDER BY i.`Interview_date` ASC, i.`Interview_time` ASC
                    """,
                    (employee_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_interviews_for_applicant(seekers_id):
        """Get all interviews for a job seeker"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        i.`Interview_id`, 
                        i.`Application_id`, 
                        i.`Interview_date`, 
                        i.`Interview_time`, 
                        i.`Meeting_link`, 
                        i.`Mode`, 
                        i.`Status`,
                        a.`Job_id`,
                        j.`Title` as job_title,
                        e.`Company_name`,
                        u.`First_name` as employer_first_name,
                        u.`Last_name` as employer_last_name
                    FROM `Interview` i
                    JOIN `Applications` a ON i.`Application_id` = a.`Application_id`
                    JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                    JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    JOIN `User` u ON e.`User_id` = u.`User_id`
                    WHERE a.`Seekers_id`=%s
                    ORDER BY i.`Interview_date` ASC, i.`Interview_time` ASC
                    """,
                    (seekers_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_interview_details(interview_id):
        """Get detailed information about an interview"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        i.`Interview_id`, 
                        i.`Application_id`, 
                        i.`Interview_date`, 
                        i.`Interview_time`, 
                        i.`Meeting_link`, 
                        i.`Mode`, 
                        i.`Status`,
                        a.`Seekers_id`,
                        a.`Job_id`,
                        j.`Title` as job_title,
                        e.`Company_name`,
                        js.`User_id` as job_seeker_user_id,
                        u.`First_name`,
                        u.`Last_name`,
                        u.`Email`,
                        eu.`First_name` as employer_first_name,
                        eu.`Last_name` as employer_last_name,
                        eu.`Email` as employer_email
                    FROM `Interview` i
                    JOIN `Applications` a ON i.`Application_id` = a.`Application_id`
                    JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                    JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    JOIN `Job_Seekers` js ON a.`Seekers_id` = js.`Seekers_id`
                    JOIN `User` u ON js.`User_id` = u.`User_id`
                    JOIN `User` eu ON e.`User_id` = eu.`User_id`
                    WHERE i.`Interview_id`=%s
                    """,
                    (interview_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update_interview(interview_id, interview_date, interview_time, meeting_link, mode, status):
        """Update interview details"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Interview`
                    SET `Interview_date`=%s, `Interview_time`=%s, `Meeting_link`=%s, `Mode`=%s, `Status`=%s
                    WHERE `Interview_id`=%s
                    """,
                    (interview_date, interview_time, meeting_link, mode, status, interview_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating interview: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def update_interview_status(interview_id, status):
        """Update interview status (completed, cancelled, no-show, etc.)"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Interview` SET `Status`=%s WHERE `Interview_id`=%s",
                    (status, interview_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating interview status: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_interview_by_id(interview_id):
        """Get single interview record"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Interview` WHERE `Interview_id`=%s",
                    (interview_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def delete_interview(interview_id):
        """Delete an interview"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM `Interview` WHERE `Interview_id`=%s",
                    (interview_id,),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting interview: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_interview_count_by_status(employee_id):
        """Get count of interviews by status for employer"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        i.`Status`, 
                        COUNT(i.`Interview_id`) as count
                    FROM `Interview` i
                    JOIN `Applications` a ON i.`Application_id` = a.`Application_id`
                    JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                    WHERE j.`Employee_id`=%s
                    GROUP BY i.`Status`
                    """,
                    (employee_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

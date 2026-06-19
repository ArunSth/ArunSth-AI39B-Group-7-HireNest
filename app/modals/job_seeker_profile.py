
from app.database import get_connection

class JobSeekerProfileModel:
    @staticmethod
    def ensure_profile_exists(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT `Seekers_id`
                    FROM `Job_Seekers`
                    WHERE `User_id`=%s
                    LIMIT 1
                    """,
                    (user_id,),
                )
                existing_profile = cur.fetchone()
                if existing_profile:
                    return existing_profile["Seekers_id"]

                cur.execute(
                    """
                    INSERT INTO `Job_Seekers` (`User_id`, `Profile_completion_percentage`)
                    VALUES (%s, 0.0)
                    """,
                    (user_id,),
                )
                conn.commit()
                return cur.lastrowid
        except Exception as e:
            print(f"Error ensuring job seeker profile exists: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def create_or_update_profile(user_id, bio, location, education, skills, experiences, resume=None):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Check if profile exists
                cur.execute("SELECT * FROM `Job_Seekers` WHERE `User_id`=%s", (user_id,))
                existing_profile = cur.fetchone()

                if existing_profile:
                    # Update existing profile
                    cur.execute(
                        """
                        UPDATE `Job_Seekers`
                        SET `Bio`=%s, `Location`=%s, `Education`=%s, `Skills`=%s, `Experiences`=%s
                        WHERE `User_id`=%s
                        """,
                        (bio, location, education, skills, experiences, user_id),
                    )
                else:
                    # Create new profile
                    cur.execute(
                        """
                        INSERT INTO `Job_Seekers` (`User_id`, `Bio`, `Location`, `Education`, `Skills`, `Experiences`)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (user_id, bio, location, education, skills, experiences),
                    )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating/updating job seeker profile: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_profile_by_user_id(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM `Job_Seekers` WHERE `User_id`=%s", (user_id,))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update_photo(user_id, photo_filename):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Job_Seekers` SET `Profile_photo`=%s WHERE `User_id`=%s",
                    (photo_filename, user_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating photo: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def update_resume(user_id, resume_path, upload_date):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Job_Seekers`
                    SET `Resume`=%s, `Resume_upload_date`=%s
                    WHERE `User_id`=%s
                    """,
                    (resume_path, upload_date, user_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating resume: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def delete_resume(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Job_Seekers`
                    SET `Resume`=NULL, `Resume_upload_date`=NULL
                    WHERE `User_id`=%s
                    """,
                    (user_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting resume: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def calculate_profile_completion(user_id):
        profile = JobSeekerProfileModel.get_profile_by_user_id(user_id)
        if not profile:
            return 0.0

        total_fields = 6  # Bio, Location, Education, Skills, Experiences, Resume
        completed_fields = 0

        if profile.get('Bio'): completed_fields += 1
        if profile.get('Location'): completed_fields += 1
        if profile.get('Education'): completed_fields += 1
        if profile.get('Skills'): completed_fields += 1
        if profile.get('Experiences'): completed_fields += 1
        if profile.get('Resume'): completed_fields += 1

        completion_percentage = (completed_fields / total_fields) * 100
        return round(completion_percentage, 2)

    @staticmethod
    def update_profile_completion(user_id, percentage):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Job_Seekers`
                    SET `Profile_completion_percentage`=%s
                    WHERE `User_id`=%s
                    """,
                    (percentage, user_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating profile completion: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

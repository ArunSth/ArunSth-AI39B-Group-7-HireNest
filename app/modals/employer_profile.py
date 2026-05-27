
from app.database import get_connection

class EmployerProfileModel:
    @staticmethod
    def create_or_update_profile(user_id, company_name, industry, description, website, logo=None):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Check if profile exists
                cur.execute("SELECT * FROM `Employee` WHERE `User_id`=%s", (user_id,))
                existing_profile = cur.fetchone()

                if existing_profile:
                    # Update existing profile
                    cur.execute(
                        """
                        UPDATE `Employee`
                        SET `Company_name`=%s, `Industry`=%s, `Description`=%s, `Website`=%s
                        WHERE `User_id`=%s
                        """,
                        (company_name, industry, description, website, user_id),
                    )
                else:
                    # Create new profile
                    cur.execute(
                        """
                        INSERT INTO `Employee` (`User_id`, `Company_name`, `Industry`, `Description`, `Website`)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (user_id, company_name, industry, description, website),
                    )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating/updating employer profile: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_profile_by_user_id(user_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM `Employee` WHERE `User_id`=%s", (user_id,))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update_logo(user_id, logo_path):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Employee`
                    SET `Logo`=%s
                    WHERE `User_id`=%s
                    """,
                    (logo_path, user_id),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating logo: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def calculate_profile_completion(user_id):
        profile = EmployerProfileModel.get_profile_by_user_id(user_id)
        if not profile:
            return 0.0

        total_fields = 5  # Company_name, Industry, Description, Website, Logo
        completed_fields = 0

        if profile.get("Company_name"): completed_fields += 1
        if profile.get("Industry"): completed_fields += 1
        if profile.get("Description"): completed_fields += 1
        if profile.get("Website"): completed_fields += 1
        if profile.get("Logo"): completed_fields += 1

        completion_percentage = (completed_fields / total_fields) * 100
        return round(completion_percentage, 2)

    @staticmethod
    def update_profile_completion(user_id, percentage):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Employee`
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

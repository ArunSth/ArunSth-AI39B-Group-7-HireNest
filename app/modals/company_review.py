from app.database import get_connection


class CompanyReviewModel:
    @staticmethod
    def create_review(seekers_id, employee_id, review_text, rating):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Company_Review` (`Seekers_id`, `Employee_id`, `Review_text`, `Rating`)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (seekers_id, employee_id, review_text, rating),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating company review: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_reviews_by_employee(employee_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT r.*, u.First_name, u.Last_name
                    FROM `Company_Review` r
                    JOIN `Job_Seekers` s ON r.Seekers_id = s.Seekers_id
                    JOIN `User` u ON s.User_id = u.User_id
                    WHERE r.Employee_id = %s
                    ORDER BY r.Created_at DESC
                    """,
                    (employee_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_review_summary(employee_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        COUNT(*) AS total_reviews,
                        AVG(Rating) AS average_rating
                    FROM `Company_Review`
                    WHERE Employee_id = %s
                    """,
                    (employee_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_review_by_id(review_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Company_Review` WHERE Review_id = %s", (review_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update_review(review_id, seekers_id, review_text, rating):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE `Company_Review`
                    SET Review_text = %s, Rating = %s
                    WHERE Review_id = %s AND Seekers_id = %s
                    """,
                    (review_text, rating, review_id, seekers_id),
                )
                conn.commit()
                return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def delete_review(review_id, seekers_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM `Company_Review` WHERE Review_id = %s AND Seekers_id = %s",
                    (review_id, seekers_id),
                )
                conn.commit()
                return cur.rowcount > 0
        finally:
            conn.close()

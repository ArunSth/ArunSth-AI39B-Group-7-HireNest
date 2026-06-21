from app.database import get_connection


class CompanyReviewModel:
    @staticmethod
    def create_review(seekers_id, employee_id, review_text, rating):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Company_Review`
                    (`Seekers_id`, `Employee_id`, `Review_text`, `Rating`, `Status`)
                    VALUES (%s, %s, %s, %s, 'Pending')
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
    def get_reviews_by_employee(employee_id, status=None):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT r.*, u.First_name, u.Last_name,
                           e.Company_name
                    FROM `Company_Review` r
                    JOIN `Job_Seekers` s ON r.Seekers_id = s.Seekers_id
                    JOIN `User` u ON s.User_id = u.User_id
                    JOIN `Employee` e ON r.Employee_id = e.Employee_id
                    WHERE r.Employee_id = %s
                """
                params = [employee_id]
                if status:
                    query += " AND COALESCE(r.Status, 'Pending') = %s"
                    params.append(status)
                query += " ORDER BY r.Created_at DESC"
                cur.execute(query, tuple(params))
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_approved_reviews_by_employee(employee_id):
        return CompanyReviewModel.get_reviews_by_employee(
            employee_id, status='Approved'
        )

    @staticmethod
    def get_review_summary(employee_id, status=None):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        COUNT(*) AS total_reviews,
                        AVG(Rating) AS average_rating
                    FROM `Company_Review`
                    WHERE Employee_id = %s
                """
                params = [employee_id]
                if status:
                    query += " AND COALESCE(Status, 'Pending') = %s"
                    params.append(status)
                cur.execute(query, tuple(params))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_review_by_id(review_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Company_Review` WHERE Review_id = %s", (
                        review_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_all_reviews_for_admin():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        r.Review_id,
                        r.Employee_id,
                        e.Company_name,
                        CONCAT(u.First_name, ' ', u.Last_name) AS Reviewer,
                        r.Rating,
                        r.Review_text,
                        COALESCE(r.Status, 'Pending') AS Status,
                        r.Created_at
                    FROM `Company_Review` r
                    JOIN `Employee` e ON r.Employee_id = e.Employee_id
                    JOIN `Job_Seekers` s ON r.Seekers_id = s.Seekers_id
                    JOIN `User` u ON s.User_id = u.User_id
                    ORDER BY r.Created_at DESC
                    """
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def update_review_status(review_id, status):
        allowed = {'Approved', 'Rejected', 'Hidden'}
        if status not in allowed:
            return False

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Company_Review` SET Status = %s WHERE Review_id = %s",
                    (status, review_id),
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception:
            conn.rollback()
            return False
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

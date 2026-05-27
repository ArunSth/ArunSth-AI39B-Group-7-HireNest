from app.database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from .base_model import create_all


class UserModel:
    """Simple user model using raw SQL and the existing PyMySQL connection.

    Methods here are minimal and intended to be used by controllers
    that already import `app.database.get_connection()`.
    """

    @staticmethod
    def ensure_schema():
        create_all()

    @staticmethod
    def create(email: str, password: str, first_name: str | None = None, last_name: str | None = None, role: str = 'user'):
        password_hash = generate_password_hash(password)
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
					INSERT INTO `User` (`Email`, `Password`, `First_name`, `Last_name`, `Role`)
					VALUES (%s,%s,%s,%s,%s)
					""",
                    (email, password_hash, first_name, last_name, role),
                )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_by_email(email: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM `User` WHERE `Email`=%s", (email,))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def verify_password(email: str, password: str) -> bool:
        user = UserModel.get_by_email(email)
        if not user:
            return False
        return check_password_hash(user['Password'], password)

    @staticmethod
    def get_by_id(user_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM `User` WHERE `User_id`=%s", (user_id,))
                return cur.fetchone()
        finally:
            conn.close()

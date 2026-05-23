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
                # ensure role exists
                cur.execute(
                    "INSERT IGNORE INTO roles (name) VALUES (%s)", (role,))
                cur.execute("SELECT id FROM roles WHERE name=%s", (role,))
                r = cur.fetchone()
                role_id = r['id'] if r else None

                cur.execute(
                    """
					INSERT INTO users (email, password_hash, first_name, last_name, role_id)
					VALUES (%s,%s,%s,%s,%s)
					""",
                    (email, password_hash, first_name, last_name, role_id),
                )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_by_email(email: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email=%s", (email,))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def verify_password(email: str, password: str) -> bool:
        user = UserModel.get_by_email(email)
        if not user:
            return False
        return check_password_hash(user['password_hash'], password)

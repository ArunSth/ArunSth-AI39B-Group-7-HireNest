import uuid
from datetime import datetime, timedelta

from app.database import get_connection


class EmailTokenModel:
    @staticmethod
    def create_token(user_id: int) -> str:
        token = uuid.uuid4().hex
        expires_at = datetime.utcnow() + timedelta(hours=1)

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO `Email_Verification_Tokens` (`User_id`, `Token`, `Expires_at`, `Is_used`) VALUES (%s, %s, %s, FALSE)",
                    (user_id, token, expires_at),
                )
                conn.commit()
            return token
        except Exception as exc:
            print(f"Error creating email token: {exc}")
            conn.rollback()
            return token
        finally:
            conn.close()

    @staticmethod
    def get_valid_token(token: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Email_Verification_Tokens` WHERE `Token`=%s AND `Is_used`=FALSE AND `Expires_at`>NOW()",
                    (token,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def mark_token_used(token_id: int) -> bool:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Email_Verification_Tokens` SET `Is_used`=TRUE WHERE `Token_id`=%s",
                    (token_id,),
                )
            conn.commit()
            return True
        except Exception as exc:
            print(f"Error marking token used: {exc}")
            conn.rollback()
            return False
        finally:
            conn.close()

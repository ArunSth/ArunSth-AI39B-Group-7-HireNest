from typing import Optional, List
from app.database import get_connection


class AdminProfileModel:

    @staticmethod
    def get_profile_by_user_id(user_id: int) -> Optional[dict]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Use 'admin_profiles' (lowercase)
                cur.execute("SELECT * FROM `admin_profiles` WHERE `User_id`=%s", (user_id,))
                return cur.fetchone()
        finally:
            conn.close()

    # ... and so on for all other methods
    # For audit logs, use 'admin_audit_log'
    # cur.execute("INSERT INTO `admin_audit_log` ...")
    

    @staticmethod
    def calculate_profile_completion(user_id: int) -> float:
        # Simple heuristic: presence of Display_name, Department, Bio
        profile = AdminProfileModel.get_profile_by_user_id(user_id) or {}
        score = 0
        if profile.get('Display_name'):
            score += 40
        if profile.get('Department'):
            score += 40
        if profile.get('Bio'):
            score += 20
        return float(min(score, 100))

    @staticmethod
    def create_or_update_profile(user_id: int, display_name: str, department: str, access_level: str = 'full', bio: Optional[str] = None, is_active: bool = True) -> bool:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Admin_Profiles` WHERE `User_id`=%s", (user_id,))
                existing = cur.fetchone()
                if existing:
                    cur.execute(
                        "UPDATE `Admin_Profiles` SET `Display_name`=%s, `Department`=%s, `Access_level`=%s, `Bio`=%s, `Is_active`=%s, `Updated_at`=CURRENT_TIMESTAMP WHERE `User_id`=%s",
                        (display_name, department,
                         access_level, bio, is_active, user_id),
                    )
                else:
                    cur.execute(
                        "INSERT INTO `Admin_Profiles` (`User_id`,`Display_name`,`Department`,`Access_level`,`Bio`,`Is_active`) VALUES (%s,%s,%s,%s,%s,%s)",
                        (user_id, display_name, department,
                         access_level, bio, is_active),
                    )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def update_profile_completion(user_id: int, percentage: float) -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Admin_Profiles` SET `Profile_completion_percentage`=%s WHERE `User_id`=%s", (percentage, user_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def update_last_login(user_id: int) -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Admin_Profiles` SET `Last_login_at`=NOW() WHERE `User_id`=%s", (user_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def record_audit_log(admin_user_id: int, action: str, target_type: Optional[str] = None, target_id: Optional[int] = None, details: Optional[str] = None) -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO `Admin_Audit_Log` (`Admin_user_id`,`Action`,`Target_type`,`Target_id`,`Details`) VALUES (%s,%s,%s,%s,%s)",
                    (admin_user_id, action, target_type, target_id, details),
                )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_audit_logs(admin_user_id: int = None, limit: int = 50) -> List[dict]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                if admin_user_id:
                    cur.execute(
                        "SELECT * FROM `Admin_Audit_Log` WHERE `Admin_user_id`=%s ORDER BY `Created_at` DESC LIMIT %s", (admin_user_id, limit))
                else:
                    cur.execute(
                        "SELECT * FROM `Admin_Audit_Log` ORDER BY `Created_at` DESC LIMIT %s", (limit,))
                return cur.fetchall()
        finally:
            conn.close()

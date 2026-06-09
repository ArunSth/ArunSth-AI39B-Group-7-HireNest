import config


def _get_pymysql():
    try:
        import pymysql
        import pymysql.cursors
    except ImportError as error:
        raise RuntimeError(
            "Missing dependency 'pymysql'. Install with: pip install pymysql"
        ) from error

    return pymysql


def get_server_connection():
    """Return a connection that can manage databases on the MySQL server."""
    pymysql = _get_pymysql()
    return pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor,
    )


def ensure_database():
    """Create the configured database if it does not already exist."""
    pymysql = _get_pymysql()
    conn = pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config.MYSQL_DATABASE}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        conn.close()


def get_connection():
    """Return a new PyMySQL connection using settings from config.

    Imports pymysql lazily so the module can be imported even when the
    database driver isn't installed. Raises a clear error if the driver
    is missing.
    """
    pymysql = _get_pymysql()

    return pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
    )


def create_default_admin(email: str = "admin@admin.com", password: str = "admin123"):
    """Create a simple default admin user if one does not already exist.

    This function follows the project's simple tutorial style: store a single
    admin `User` row with basic fields. It is safe to call on startup and will
    not raise if the table doesn't yet exist.
    """
    try:
        from werkzeug.security import generate_password_hash
    except Exception:
        # If werkzeug isn't available, skip seeding to avoid startup failure.
        return

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Check existing by Email column on `User` table
            cur.execute("SELECT * FROM `User` WHERE `Email`=%s", (email,))
            row = cur.fetchone()
            if row:
                return

            hashed = generate_password_hash(password)
            cur.execute(
                "INSERT INTO `User` (`First_name`,`Last_name`,`Email`,`Password`,`Role`) VALUES (%s,%s,%s,%s,%s)",
                ("Admin", "", email, hashed, "admin"),
            )
        conn.commit()
    except Exception:
        # Don't let seeding break application startup.
        return
    finally:
        if conn:
            conn.close()

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

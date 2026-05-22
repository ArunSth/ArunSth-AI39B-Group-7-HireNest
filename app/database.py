import config


def get_connection():
    """Return a new PyMySQL connection using settings from config.

    Imports pymysql lazily so the module can be imported even when the
    database driver isn't installed. Raises a clear error if the driver
    is missing.
    """
    try:
        import pymysql
        import pymysql.cursors
    except ImportError as e:
        raise RuntimeError(
            "Missing dependency 'pymysql'. Install with: pip install pymysql"
        ) from e

    return pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
    )
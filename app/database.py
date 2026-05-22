import pymysql
import pymysql.cursors
import config


def get_connection():
    """Return a new PyMySQL connection using settings from config."""
    return pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
    )
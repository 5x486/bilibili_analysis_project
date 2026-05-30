import pymysql
from config import Config


def conn():
    """Create database connection and cursor."""
    con = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        db=Config.DB_NAME,
        charset='utf8mb4',
    )
    cur = con.cursor()
    return con, cur


def close(con, cur):
    """Close cursor and connection."""
    cur.close()
    con.close()


def query(sql, params=None):
    """Execute a SELECT query and return all results."""
    con, cur = conn()
    cur.execute(sql, params)
    res = cur.fetchall()
    close(con, cur)
    return res


def execute(sql, params=None):
    """Execute an INSERT/UPDATE/DELETE query and commit."""
    con, cur = conn()
    cur.execute(sql, params)
    con.commit()
    close(con, cur)

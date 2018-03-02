import MySQLdb
try:
    import sqlite3
except ImportError:
    print("sqlite3 is not installed. You can only use MySQL.")


def sqlite_connect_db(dbname):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    return conn, cur


def sqlite_create_table(conn, cur):
    print("creating table...")
    cur.execute("""CREATE TABLE IF NOT EXISTS distance (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        macaddr    TEXT,
        pwr        INTEGER,
        distance   INTEGER,
        rpimac     TEXT
        )""")
    conn.commit()


def sqlite_insert_data(conn, cur, data):
    cur.execute("""
        INSERT INTO distance VALUES(NULL,?,?,?,?)
        """, (data["MAC"], data["PWR"], data["DIST"], data["RPI_MAC"]))
    conn.commit()


def mysql_connect(host, user, passwd, db, charset='utf8'):
    conn = MySQLdb.connect(host, user, passwd, db, charset=charset)
    cur = conn.cursor()
    return conn, cur


def mysql_create_table(conn, cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS distance(
             id       INT NOT NULL AUTO_INCREMENT,
             macaddr  VARCHAR(128),
             pwr      INTEGER,
             distance INTEGER,
             rpimac   VARCHAR(128),
             PRIMARY KEY (id)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    conn.commit()


def mysql_insert_data(conn, cur, data):
    cur.execute("""
      INSERT INTO distance VALUES (NULL, %s, %s, %s, %s)
    """, (data["MAC"], data["PWR"], data["DIST"], data["RPI_MAC"]))
    conn.commit()


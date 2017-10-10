#!/usr/bin/env python3
import csv
import time
import sys
import traceback
import math
import sqlite3
from enum import Enum

MAC = 0
INI = 1
FIN = 2
PWR = 3 
DATA = 4
ESSID = 5
DIST = 6


def create_table(conn, cur):
    cur.execute("""CREATE TABLE distance (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        macaddr    TEXT,
        pwr        INTEGER,
        distance   INTEGER
        )""")
    conn.commit()


def getdb(dbname): 
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    return (conn, cur)


def table_isexist(conn, cur):
    cur.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE TYPE='table' AND name='distance'
        """)
    if cur.fetchone()[0] == 0:
        return False
    return True  


def insert_data(conn, cur, data):
    cur.execute("""
        INSERT INTO distance VALUES(NULL,?,?,?)
        """, (data[MAC], data[PWR], data[DIST],))
    conn.commit()


def main(argv):
    filename = argv[0] + "-01.csv"
    essid = argv[1]
    interval = float(argv[2])
    dbname = 'distance.db'
    (conn, cur) = getdb(dbname)
    if table_isexist(conn, cur) == False:
        print("not exist")
        create_table(conn, cur)
    
    while True:
        try:
            with open(filename, 'r', newline='') as fin:
                reader = csv.reader(fin)
                header = next(reader)
                for row in reader:
                    if len(row) > ESSID and row[ESSID].lstrip() == essid:
                        with open("output", "a") as fout:
                            # 測定不能なホストを飛ばす
                            if int(row[PWR]) == -1: 
                                continue
                            distance = math.exp(1) ** (-1*(int(row[PWR])+36)/8.7)
                            row.append(distance)
                            insert_data(conn, cur, row)
            time.sleep(interval)
        except IOError as e:
            print("IOError")
            sys.exit(1)

        except KeyboardInterrupt:
            sys.exit(0)

        except:
            print(traceback.format_exc()) 
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

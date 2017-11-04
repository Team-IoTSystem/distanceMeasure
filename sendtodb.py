#!/usr/bin/env python3
import csv
import time
import sys
import traceback
import math
import sqlite3
import uuid

MAC = 0
INI = 1
FIN = 2
PWR = 3 
DATA = 4
BSSID = 5
DIST = 7
RPI_MAC = 8

MINCUL = 6

def create_table(conn, cur):
    cur.execute("""CREATE TABLE distance (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        macaddr    TEXT,
        pwr        INTEGER,
        distance   INTEGER,
        rpimac     TEXT
        )""")
    conn.commit()


def getdb(dbname): 
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    return (conn, cur)


def isexist(conn, cur):
    cur.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE TYPE='table' AND name='distance'
        """)
    if cur.fetchone()[0] == 0:
        return False
    return True  


def insert_data(conn, cur, data):
    cur.execute("""
        INSERT INTO distance VALUES(NULL,?,?,?,?)
        """, (data[MAC], data[PWR], data[DIST], data[RPI_MAC]))
    conn.commit()


def get_distance(pwr):
    return int(math.exp(1) ** (-1*(int(pwr)+40)/9))


def main(argv):
    filename = argv[0]
    essid = argv[1] #可読なAPの識別子
    bssid = '' #APのMACaddr
    interval = float(argv[2])
    dbname = 'distance.db'
    (conn, cur) = getdb(dbname)
    if isexist(conn, cur) == False:
        create_table(conn, cur)
    
    while True:
        try:
            with open(filename, 'r', newline='') as fin:
                reader = csv.reader(fin)
                header = next(reader)
                # APのBSSIDを特定
                for row in reader:
                    if row[-1].lstrip() == essid:
                        bssid = row[0].lstrip()
                        break

                for row in reader:
                    if len(row) >= MINCUL and\
                                    row[BSSID].lstrip() == bssid and\
                        # 測定不能なホストを飛ばす
                        if int(row[PWR]) == -1:
                            continue
                        distance = get_distance(row[PWR])
                        rpi_mac = hex(uuid.getnode())[2:]
                        row.append(distance)
                        row.append(rpi_mac)
                        insert_data(conn, cur, row)

            time.sleep(interval)

        except KeyboardInterrupt:
            sys.exit(0)

        except:
            print(traceback.format_exc()) 
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

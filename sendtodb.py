#!/usr/bin/env python3
import csv
import time
import sys
import traceback
import math
import sqlite3
import uuid
import json

MAC = 0
INI = 1
FIN = 2
PWR = 3 
PAC = 4
BSSID = 5
DIST = 7
RPI_MAC = 8

MINCUL = 6

def create_table(conn, cur):
    print("creating table...")
    cur.execute("""CREATE TABLE distance (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        macaddr    TEXT,
        pwr        INTEGER,
        distance   INTEGER,
        rpimac     TEXT
        )""")
    conn.commit()


def get_db(dbname):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    return (conn, cur)


def is_exist(conn, cur):
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
        """, (data["MAC"], data["PWR"], data["DIST"], data["RPI_MAC"]))
    conn.commit()


def get_distance(pwr):
    return int(math.exp(1) ** (-1*(int(pwr)+40)/9))


def main(argv):
    filename = argv[0]
    essid = argv[1] #可読なAPの識別子
    bssid = '' #APのMACaddr
    interval = float(argv[2])
    dbname = 'distance.db'
    colmAP = ["BSSID", "FIR", "LAS", "CHN", "SPD", "PRY", "CIP", "ATH", "PWR", "BCN", "IV", "IP", "LEN", "ESSID", "KEY"]
    colmSTA = ["MAC", "FIR", "LAS", "PWR", "PAC", "BSSID", "ESSID", "DIST", "RPI_MAC"]

    rpi_mac = hex(uuid.getnode())[2:]
    (conn, cur) = get_db(dbname)
    if not is_exist(conn, cur):
        create_table(conn, cur)
    
    while True:
        try:
            with open(filename, 'r', newline='') as fin:
                reader = csv.DictReader(fin, colmAP)
                # APのBSSIDを特定
                for row in reader:
                    if row["BSSID"].lstrip() == "Station MAC":
                        break
                    if row["ESSID"].lstrip() == essid:
                        bssid = row["BSSID"].lstrip()

                reader.fieldnames = colmSTA
                for row in reader:
                    if row["BSSID"].lstrip() == bssid:
                        # 測定不能なホストを飛ばす
                        if int(row["PWR"]) == -1:
                            continue
                        distance = get_distance(row["PWR"])
                        row["DIST"] = distance
                        row["RPI_MAC"] = rpi_mac
                        insert_data(conn, cur, row)
                        print("database was updated!")

            time.sleep(interval)

        except KeyboardInterrupt:
            sys.exit(0)

        except:
            print(traceback.format_exc()) 
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

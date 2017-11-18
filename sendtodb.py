#!/usr/bin/env python3
import csv
import time
import sys
import traceback
import math
import sqlite3
import uuid
import json
import requests


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


def post_data(data, server, endpoint):
    dist = "http://" + server + endpoint
    headertype = {"Content-Type": "application/json"}
    requests.post(dist, json.dumps(data), headers=headertype)


def main():
    filename = sys.argv[1]
    essid = sys.argv[2] #可読なAPの識別子
    bssid = '' #APのMACaddr
    interval = float(sys.argv[3])
    server = sys.argv[4] # サーバーのIP
    endpoint = sys.argv[5]
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
                    if row["BSSID"].strip() == "Station MAC":
                        break
                    if row["ESSID"].strip() == essid:
                        bssid = row["BSSID"].strip()

                reader.fieldnames = colmSTA
                for row in reader:
                    if row["BSSID"].strip() == bssid:
                        # 測定不能なホストを飛ばす
                        if int(row["PWR"]) == -1:
                            continue
                        distance = get_distance(row["PWR"])
                        row["DIST"] = distance
                        row["RPI_MAC"] = rpi_mac
                        data = {"MAC": row["MAC"], "PWR": int(row["PWR"]), "DIST": row["DIST"], "RPI_MAC": row["RPI_MAC"]}
                        insert_data(conn, cur, data)
                        post_data(data, server, endpoint)
                        print("database was updated!")

            time.sleep(interval)

        except KeyboardInterrupt:
            sys.exit(0)

        except:
            print(traceback.format_exc()) 
            sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import csv
import time
import sys
import traceback
import math
import uuid
import json
import requests
import dbcontroller
from certification_data import *


def get_distance(pwr):
    border = 10
    distance = int(math.exp(1) ** (-1*(int(pwr)+40)/9))
    if distance < border:
        distance = border
    return distance


def post_data(data, server_ip, endpoint):
    dist = "http://" + server_ip + endpoint
    headertype = {"Content-Type": "application/json"}
    requests.post(dist, json.dumps(data), headers=headertype)


def main():
    debug = True
    filename = sys.argv[1]
    essid = sys.argv[2]
    bssid = ''
    interval = float(sys.argv[3])
    server_ip = sys.argv[4]
    endpoint = sys.argv[5]
    colmAP = ["BSSID", "FIR", "LAS", "CHN", "SPD", "PRY", "CIP", "ATH", "PWR", "BCN", "IV", "IP", "LEN", "ESSID", "KEY"]
    colmSTA = ["MAC", "FIR", "LAS", "PWR", "PAC", "BSSID", "ESSID", "DIST", "RPI_MAC"]

    rpi_mac = hex(uuid.getnode())[2:]
    # (sqlite_conn, sqlite_cur) = dbcontroller.sqlite_connect_db(dbname)
    (mysql_conn, mysql_cur) = dbcontroller.mysql_connect(host, user, passwd, db, charset)
    # dbcontroller.sqlite_create_table(sqlite_conn, sqlite_cur)
    dbcontroller.mysql_create_table(mysql_conn, mysql_cur)
    
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
                    if row["BSSID"] and row["BSSID"].strip() == bssid:
                        # 測定不能なホストを飛ばす
                        if int(row["PWR"]) == -1:
                            continue
                        distance = get_distance(row["PWR"])
                        row["DIST"] = distance
                        row["RPI_MAC"] = rpi_mac
                        data = {"MAC": row["MAC"], "PWR": int(row["PWR"]), "DIST": row["DIST"], "RPI_MAC": row["RPI_MAC"]}
                        # dbcontroller.sqlite_insert_data(sqlite_conn, sqlite_cur, data)
                        dbcontroller.mysql_insert_data(mysql_conn, mysql_cur, data)
                        # post_data(data, server_ip, endpoint)
                        if debug and data["MAC"] == "84:89:AD:8D:85:F6":
                            print("MAC:{}, PWR:{}".format(data["MAC"], data["PWR"]))
            time.sleep(interval)

        except KeyboardInterrupt:
            sys.exit(0)

        except Exception:
            print(traceback.format_exc()) 
            sys.exit(1)


if __name__ == "__main__":
    main()

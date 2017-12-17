import dbcontroller
from certification_data import *


def main():
    conn, cur = dbcontroller.mysql_connect(host, user, passwd, db, charset)
    if conn:
        print("succeeded")

if __name__ == '__main__':
    main()

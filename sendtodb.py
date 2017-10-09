#!/usr/bin/env python3
import csv
import time
import sys
import traceback
def main(argv):
    filename = argv[0] + "-01.csv"
    essid = argv[1]
    interval = float(argv[2])
    essid_index = 5
    pwr_index = 3 
    while True:
        try:
            with open(filename, 'r', newline='') as fin:
                reader = csv.reader(fin)
                header = next(reader)
                for row in reader:
                    if len(row) > essid_index:
                        #print(row[essid_index])
                        if row[essid_index].lstrip() == essid:
                            with open("output", "a") as fout:
                                fout.writelines(row)
                                fout.write("\n")
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

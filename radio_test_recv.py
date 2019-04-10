#!/usr/bin/python3

import sys
import os
import time
import farmradio
import random
def main():

    fr = farmradio.FarmRadio()
    print("Hello - Testing Radio Recieving")

    while True:
        try:
            raw_data = fr.recv_raw(5.0)
            if raw_data is not None:
                print("Data: %s" % raw_data)
                time.sleep(0.5)
            else:
                print("No Data")
        except KeyboardInterrupt:
            print("Keyboard Exit")
            sys.exit(0)
        time.sleep(0.1)


if __name__ == "__main__":
    main()

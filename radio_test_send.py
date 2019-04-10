#!/usr/bin/python3

import sys
import os
import time
import farmradio
import random
def main():

    fr = farmradio.FarmRadio()

    print("Hello - Testing Radio Sending")

    while True:
        if random.randint(1,6) == 1:
            print("Random Send: %s" % curmsg)
            curmsg = int(time.time())
            fr.send_raw("Hey, how's it going - %s" % curmsg)
        time.sleep(1)


if __name__ == "__main__":
    main()

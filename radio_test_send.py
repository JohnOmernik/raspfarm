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
            curmsg = int(time.time())
            for i in range(5):
                print("Random Send Attempt: %s -  %s" % (i, curmsg))
                fr.send_raw("Hey, how's it going - Send: %s - %s" % (i,curmsg))
                time.sleep(0.1)
        time.sleep(1)


if __name__ == "__main__":
    main()

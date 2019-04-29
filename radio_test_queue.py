#!/usr/bin/python3

import sys
import os
import time
import farmqueue
import random
import json
import socket
def main():


    f = open("farmradio.cfg", 'r')
    rawconf = f.read().strip()
    conf = json.loads(rawconf)
    f.close()


    myname = socket.gethostname()
    print("Radio Type is %s" % conf['radiotype'])
    print("Server is %s" % conf['server'])
    if myname == conf['server']:
        server = True
        print("Looks like we are the server!")
    else:
        server = False
    if conf['debug'] == 1:
        print("Debug is true")
        mydebug = True
    else:
        mydebug = False
    senders = []
    fq = farmqueue.FarmQueue(conf['radiotype'], debug=mydebug)

    print("Hello - Testing Radio Sending and Queing")

    while True:
        try:
            print("top of main loop")
            msg = fq.getmsg()
            if msg is not None:
                print("Message: %s" % msg)
                time.sleep(0.5)
            else:
                print("No Data")
        except KeyboardInterrupt:
            print("Keyboard Exit")
            sys.exit(0)
        if random.randint(1,6) <= 2:
            if server == False:
                require_ack = bool(random.randint(0,1))
                print("Sending message to server, require ack: %s" % require_ack)
                fq.sendmsg(conf['server'], "A great message from %s to %s" % (myname, conf['server']), require_ack)
            time.sleep(0.5)
        time.sleep(0.5)


if __name__ == "__main__":
    main()

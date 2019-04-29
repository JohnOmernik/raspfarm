#!/usr/bin/python3

import sys
import os
import time
import farmqueue
import random
import gevent
import json
import socket

mydebug = False

fq = None
server = False
conf = ""
myname = ""
senders = []
def main():
    global mydebug
    global fq
    global myname
    global server
    global conf
    global senders
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
        print("No server for %s" % myname)
        server = False
    if conf['debug'] == 1:
        print("Debug is true")
        mydebug = True
    else:
        mydebug = False

    fq = farmqueue.FarmQueue(conf['radiotype'], debug=mydebug)
    print("Hello - Testing Radio Sending and Queing")
    gevent.joinall([
        gevent.spawn(procmsg),
        gevent.spawn(fq.recvmsgs),
        gevent.spawn(fq.sendmsgs)
        ]
        )


def procmsg():
    global fq
    global mydebug
    global conf
    global myname
    global server
    global senders
    while True:
        try:
            if mydebug:
                print("top of main loop")
            msg = fq.getmsg()
            if msg is not None:
                try:
                    armsg = msg.split("~")
                    sender = armsg[2]
                    if sender not in senders:
                        senders.append(sender)
                except:
                    pass
                print("Message: %s" % msg)
                time.sleep(0.5)
            else:
                print("No Data")
            gevent.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard Exit")
            sys.exit(0)
        gevent.sleep(1)
        if random.randint(1,6) <= 2:
            if server == False:
                require_ack = bool(random.randint(0,1))
                print("Sending message to server, require ack: %s" % require_ack)
                fq.sendmsg(conf['server'], "A great message from %s to %s" % (myname, conf['server']), require_ack)
            else:
                if len(senders) > 0:
                    thissender = random.choice(senders)
                    require_ack = bool(random.randint(0,1))
                    print("Sending message from server to %s" % thissender)
                    fq.sendmsg(thissender, "A message from the server", require_ack)
                else:
                    print("No Senders yet")

            time.sleep(0.5)
        time.sleep(0.5)


if __name__ == "__main__":
    main()

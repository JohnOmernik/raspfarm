#!/usr/bin/python3

import sys
import os
import time
import farmqueue
import random
import gevent
import json
import socket

conf = {}
fq = None
conf = ""
myname = ""
senders = []
def main():
    global fq
    global myname
    global conf
    global senders
    f = open("farmradio.cfg", 'r')
    rawconf = f.read().strip()
    conf = json.loads(rawconf)
    f.close()
    myname = socket.gethostname().lower()

    print("Radio Type is %s" % conf['radiotype'])
    print("Server is %s" % conf['servername'])


    if myname.lower() == conf['servername'].lower():
        conf['server'] = True
        print("Looks like we are the server!")
    else:
        conf['server'] = False

    if conf['debug'] == 1:
        print("Debug is true")
        conf['debug'] = True
    else:
        conf['debug'] = False

    fq = farmqueue.FarmQueue(debug=conf['debug'], timeout=conf['timeout'], resend_delay=conf['resend_delay'], radio_conf=conf)

    print("Hello - Testing Radio Sending and Queing")

    gevent.joinall([
        gevent.spawn(procmsg),
        gevent.spawn(fq.recvmsgs),
        gevent.spawn(fq.sendmsgs)
        ]
        )

def procmsg():
    global fq
    global conf
    global myname
    global senders
    while True:
        try:
#            if conf['debug']:
#                print("top of main loop")
            msg = fq.getmsg()
            if msg is not None:
                try:
                    armsg = msg.split("~")
                    sender = armsg[2].lower()
                    print("<<<<< Message In: %s" % msg)
                    if sender not in senders:
                        senders.append(sender)
                except:
                    print("<!<!< - Odd Message: %s" % msg)
            else:
                print("***** - No Data")
            gevent.sleep(1)

        except KeyboardInterrupt:
            print("!!!!!!!!!!!!!!! Keyboard Exit")
            sys.exit(0)
        gevent.sleep(1)

        if random.randint(1,6) <= 2:
            if conf['server'] == False:
                require_ack = True
                print(">>>>> Sending message to server, require ack: %s" % require_ack)
                fq.sendmsg(conf['servername'], "A worker message to the server from %s to %s" % (myname, conf['servername']), require_ack)
            else:
                if len(senders) > 0:
                    thissender = random.choice(senders)
                    require_ack = True
                    print(">>>>> Sending message from server to %s" % thissender)
                    fq.sendmsg(thissender, "A message from the server", require_ack)
                else:
                    print("***** No Senders yet - Server not sending message")

            gevent.sleep(0.5)
        gevent.sleep(0.5)


if __name__ == "__main__":
    main()

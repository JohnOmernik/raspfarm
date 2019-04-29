#!/usr/bin/python3

import sys
import os
import time
try:
    import farmradio
except:
    print("farmradio not imported")
try:
    import farmradio_usb
except:
    print("farmradio_usb not imported")
import random
import socket
import hashlib
import threading
import gevent
from collections import OrderedDict
def main():
    print("Queue Testing")



class FarmQueue():


    fr = None
    radio = "hat" # or usb
    send_queue = OrderedDict()
    recv_queue = OrderedDict()
    resend_delay = 10 # Number of seconds to wait between resending of messages
    myname = ""
    timeout = 1.0
    debug = False
    def __init__(self, radio, debug=False):
        self.debug = debug
        self.radio = radio
        self.myname = socket.gethostname()

        if self.radio == "hat":
            self.fr = farmradio.FarmRadio()
        else:
            self.fr = farmradio_usb.FarmRadio()

        gevent.joinall([
            gevent.spawn(self.sendmsgs),
            gevent.spawn(self.recvmsgs)
        ])
    def sendmsgs(self):
        while True:
            if self.debug:
                print("Top of sendmsgs")
            for msghash in self.send_queue.keys():
                curtime = int(time.time())
                if (self.send_queue[msghash]['ack'] == False and self.send_queue[msghash]['require_ack'] == True) or self.send_queue[msghash]['last_send'] == 0:
                    if curtime - self.send_queue[msghash]['last_send'] > self.resend_delay: 
                        self.fr.send_raw(self.send_queue[msghash]['msg'])
                        self.send_queue[msghash]['last_send'] = curtime
                gevent.sleep(2)
            gevent.sleep(2)
    def recvmsgs(self):
        while True:
            if self.debug:
                print("Top of recvmsgs")
            msg = self.fr.recv_raw(self.timeout)
            if msg != "":
                msgar = msg.split("~")
                if len(msgar) == 5:
                    msgts = msgar[0]
                    msgto = msgar[1]
                    msgfrom = msgar[2]
                    msgack = msgar[3]
                    msgstr = msgar[4]
                    if msgto == self.myname:
                        msghash = hashlib.md5(msg).hexdigest()
                        if msghash in self.recv_queue:
                            if msgack == 1:
                                self.sendack(msgto, msghash)
                        else:
                            self.recv_query[msghash] = {'from': msgfrom, 'msg': msg, 'processed': False}
                            if msgack == 1:
                                send.sendack(msgto, msghash)
                else:
                    print("Odd message: %s" % msg)
            gevent.sleep(0.5)

    #msg: ts~recp~sender~require_ack (0 or 1), msg

    # Ack a message we have recieved
    def sendack(self, msgto, msghash):
        mymsg = "ack:%s" % (msghash)
        self.sendmsg(msgt, mymsg, False)

    def sendmsg(self, msgto, base_msg, require_ack):
        print("Sending msg")
        curtime = int(time.time())
        if require_ack == True:
            msgack = 1
        else:
            msgack = 0
        strmsg = "%s~%s~%s~%s~%s" % (curtime, msgto, self.myname, msgack, base_msg)
        msghash = hashlib.md5(strmsg).hexdigest()
        self.send_queue[msghash] = {'to': to, 'msg': strmsg, 'last_send': 0, 'require_ack': require_ack, "ack": False}


if __name__ == "__main__":
    main()

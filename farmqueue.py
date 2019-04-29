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
    def getmsg(self):
        for msg in self.recv_queue.keys():
            if self.recv_queue[msg]['processed'] == False:
                self.recv_queue[msg]['processed'] = True
                gevent.sleep(1)
                return self.recv_queue[msg]['msg']
        gevent.sleep(1)
        return None

    def sendmsgs(self):
        while True:
            if self.debug:
                print("Top of sendmsgs: No. of Msgs in Queue: %s" % len(self.send_queue.keys()))
            queue = OrderedDict(self.send_queue)
            for msghash in queue.keys():
                if self.debug:
                    print("processing: %s" % msghash)
                curtime = int(time.time())
                if (self.send_queue[msghash]['ack'] == False and self.send_queue[msghash]['require_ack'] == True) or self.send_queue[msghash]['last_send'] == 0:
                    if curtime - self.send_queue[msghash]['last_send'] > self.resend_delay: 
                        print("Sending %s" % msghash)
                        self.fr.send_raw(self.send_queue[msghash]['msg'])
                        self.send_queue[msghash]['last_send'] = curtime
                        if self.send_queue['msghash']['require_ack'] == False:
                            if self.debug:
                                print("Message %s sent, no ack required - removing from queue")
                                del self.send_queue[msghash]
                elif self.send_queue[msghash]['ack'] == True:
                    if self.debug:
                        print("Message %s acked - removing from queue" % msghash)
                    del self.send_queue[msghash]
                gevent.sleep(0.5)
            gevent.sleep(0.5)
    def recvmsgs(self):
        while True:
            if self.debug:
                print("Top of recvmsgs")
            msg = self.fr.recv_raw(self.timeout)
            if msg != "" and msg is not None:
                msgar = msg.split("~")
                if len(msgar) == 5:
                    msgts = msgar[0]
                    msgto = msgar[1]
                    msgfrom = msgar[2]
                    msgack = msgar[3]
                    msgstr = msgar[4]
                    if msgto == self.myname:
                        msghash = hashlib.md5(msg.encode("UTF-8")).hexdigest()
                        if msghash in self.recv_queue:
                            if msgack == 1:
                                self.sendack(msgto, msghash)
                        else:
                            self.recv_queue[msghash] = {'from': msgfrom, 'msg': msg, 'processed': False}
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
        msghash = hashlib.md5(strmsg.encode("UTF-8")).hexdigest()
        self.send_queue[msghash] = {'to': msgto, 'msg': strmsg, 'last_send': 0, 'require_ack': require_ack, "ack": False}


if __name__ == "__main__":
    main()

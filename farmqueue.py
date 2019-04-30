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
    send_queue = OrderedDict()
    recv_queue = OrderedDict()

    radio = "" # hat or usb loaded with __init__
    resend_delay = 10 # Number of seconds to wait between resending of messages
    myname = ""
    timeout = 1.0
    debug = False

    def __init__(self, radio, debug=False, timeout=1.0, resend_delay=5):
        self.debug = debug
        self.radio = radio
        self.timeout = timeout
        self.resend_delay = resend_delay
        self.myname = socket.gethostname().lower()

        if self.radio == "hat":
            self.fr = farmradio.FarmRadio(timeout=self.timeout)
        else:
            self.fr = farmradio_usb.FarmRadio(timeout=self.timeout)

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
                        if self.send_queue[msghash]['require_ack'] == False:
                            if self.debug:
                                print("^^^^^ Message %s sent, no ack required - removing from queue" % msghash)
                                del self.send_queue[msghash]
                elif self.send_queue[msghash]['ack'] == True:
                    if self.debug:
                        print("^^^^^ Message %s acked - removing from queue" % msghash)
                    del self.send_queue[msghash]
                gevent.sleep(0.5)
            gevent.sleep(0.5)

    def recvmsgs(self):
        while True:
            if self.debug:
                pass
                #print("Top of recvmsgs")
            msg, snr = self.fr.recv_raw()
            if msg != "" and msg is not None:
                msgar = msg.split("~")
                if len(msgar) == 5:
                    msgts = msgar[0]
                    msgto = msgar[1].lower()
                    msgfrom = msgar[2].lower()
                    msgack = int(msgar[3])
                    msgstr = msgar[4]
                    if msgto.lower() == self.myname.lower(): # If the dest address is the same as me, then accept the messages
                        if self.debug:
                            print("##### Got a FQ message at %s signal: %s" % (msg, snr))
                        if msgstr.find("ack:") >= 0:    # Check to see if this is an acked message
                            msghash = msgstr.split(":")[1]
                            if self.debug:
                                print("@@@@@@ Recv ACK for message %s" % msghash)
                            if msghash in self.send_queue:
                                self.send_queue[msghash]['ack'] = True
                            else:
                                print("@!@!@ Message ack sent, but we don't have this message in queue")
                            # this is a Message ack
                        else: # Normal message
                            msghash = hashlib.md5(msg.encode("UTF-8")).hexdigest()
                            if msghash in self.recv_queue: # We've already gotten this, so let's not re process it, but we will resend ack if needed
                                if msgack == 1:
                                    self.sendack(msgfrom, msghash)
                            else:
                                self.recv_queue[msghash] = {'from': msgfrom, 'msg': msg, 'processed': False}
                                if msgack == 1:
                                    self.sendack(msgfrom, msghash)
                    else:
                        pass
                        #print("!!!>> Message not for me: %s vs. %s" % (msgto.lower(), self.myname.lower()))
                else:
                    print("Odd message: %s" % msg)
            gevent.sleep(0.5)

    #msg: ts~recp~sender~require_ack (0 or 1), msg

    # Ack a message we have recieved
    def sendack(self, msgto, msghash):
        if self.debug:
            print("@@@@@ Sending msgack to %s for %s" % (msgto,msghash))
        mymsg = "ack:%s" % (msghash)
        self.sendmsg(msgto, mymsg, False)

    def sendmsg(self, msgto, base_msg, require_ack):
        curtime = int(time.time())
        if require_ack == True:
            msgack = 1
        else:
            msgack = 0
        strmsg = "%s~%s~%s~%s~%s" % (curtime, msgto, self.myname, msgack, base_msg)
        msghash = hashlib.md5(strmsg.encode("UTF-8")).hexdigest()

        if self.debug:
            print("##### Putting msg %s in send_queue: %s" % (msghash, strmsg))

        self.send_queue[msghash] = {'to': msgto, 'msg': strmsg, 'last_send': 0, 'require_ack': require_ack, "ack": False}


if __name__ == "__main__":
    main()

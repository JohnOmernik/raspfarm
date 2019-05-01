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
    radio_conf = {}
    resend_delay = None
    myname = ""
    timeout = None
    debug = False

    def __init__(self,  debug=False, timeout=1.0, resend_delay=5, send_prune_window=60, recv_prune_window=60, radio_conf={"radio_freq_mhz": 915.5, "radio_tx_pwr": 20, "radio_serial_port": "spi", "radio_mode": "lora", "radio_spread_factor": 7, "radio_crc": False, "radio_cr": 5, "radio_bw": 125, "radio_wdt": 0}):
        self.radio_conf = radio_conf
        self.recv_prune_window = recv_prune_window # Number of seconds to leave a processed message  after the last ack in recv queue
        self.send_prune_window = send_prune_window # Number of seconds since first send (without an ack) to give up on message
        self.debug = debug
        self.timeout = timeout
        self.resend_delay = resend_delay
        self.myname = socket.gethostname().lower()

        if self.radio_conf['radio_serial_port']  == "spi":
            self.fr = farmradio.FarmRadio(debug=self.debug, timeout=self.timeout, radio_conf=self.radio_conf)
        else:
            self.fr = farmradio_usb.FarmRadio(debug=self.debug, timeout=self.timeout, radio_conf=self.radio_conf)

    def getmsg(self):
        queue = OrderedDict(self.recv_queue)
        for msg in queue.keys():
            curtime = int(time.time())
            if self.recv_queue[msg]['ts_proc'] == 0:
                self.recv_queue[msg]['ts_proc'] = curtime
                gevent.sleep(1)
                return self.recv_queue[msg]['msg']
            elif self.recv_queue[msg]['ts_proc'] > 0:
                if curtime - self.recv_queue[msg]['ts_lastack'] >= self.recv_prune_window:
                    del self.recv_queue[msg]

        gevent.sleep(1)
        return None

    def sendmsgs(self):
        while True:
            if self.debug:
                print("_______________________________________________________Send Queue: %s" % len(self.send_queue.keys()))
            queue = OrderedDict(self.send_queue)
            for msghash in queue.keys():
                if self.debug:
                    print("processing: %s" % msghash)
                curtime = int(time.time())
                if (self.send_queue[msghash]['ack'] == False and self.send_queue[msghash]['require_ack'] == True) or self.send_queue[msghash]['last_send'] == 0:
                   if curtime - self.send_queue[msghash]['last_send'] > self.resend_delay:
                        if self.send_queue[msghash]['first_send'] == 0:
                            self.send_queue[msghash]['first_send'] = curtime
                        self.fr.send_raw(self.send_queue[msghash]['msg'])
                        self.send_queue[msghash]['last_send'] = curtime
                        print("Sending %s - %s - Ack Required: %s" % (msghash, self.send_queue[msghash]['msg'], self.send_queue[msghash]['require_ack']))
                        if curtime - self.send_queue[msghash]['first_send'] >= self.send_prune_window:
                            print(">>>>> !!!!!!! >>>>> !!!!! - Message %s was first sent %s and it's now %s, longer then the send_prune_window(%s): Removing" % (msghash, self.send_queue[msghash]['first_send'], curtime, self.send_prune_window))
                            del self.send_queue[msghash]
                        elif self.send_queue[msghash]['require_ack'] == False:
                            del self.send_queue[msghash]
                elif self.send_queue[msghash]['ack'] == True:
                    del self.send_queue[msghash]
                gevent.sleep(0.5)
            gevent.sleep(0.5)

    def recvmsgs(self):
        while True:
            if self.debug:
                print("_______________________________________________________Recv Queue: %s" % len(self.recv_queue.keys()))
            curtime = int(time.time())
            msg, snr = self.fr.recv_raw()
            if msg != "" and msg is not None:
                msgar = msg.split("~")
                if len(msgar) == 5:
                    try:
                        msgts = msgar[0]
                        msgto = msgar[1].lower()
                        msgfrom = msgar[2].lower()
                        msgack = int(msgar[3])
                        msgstr = msgar[4]
                    except:
                        print("----- Message did not split into 5 parts: %s" % msg)
                        msgto = None
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
                                    self.recv_queue[msghash]['ts_lastack'] = curtime
                            else:
                                self.recv_queue[msghash] = {'from': msgfrom, 'ts_recv': curtime, 'ts_proc': 0, 'ts_lastack': 0, 'msg': msg}
                                if msgack == 1:
                                    self.sendack(msgfrom, msghash)
                                    self.recv_queue[msghash]['ts_lastack'] = curtime

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

        self.send_queue[msghash] = {'to': msgto, 'msg': strmsg, 'last_send': 0, 'first_send': 0,  'require_ack': require_ack, "ack": False}


if __name__ == "__main__":
    main()

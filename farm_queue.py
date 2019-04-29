#!/usr/bin/python3

import sys
import os
import time
import farmradio
import farmradio_usb
import random
import socket
import hashlib
from collections import OrderedDict
def main():
    print("Queue Testing")





class FarmQueue():


    fr = None
    radio = "hat" # or usb
    send_queue = OrderedDict()
    recv_queue = OrderedDict()
    myname = ""


    def __init__(self, radio):
        self.radio = radio
        self.myname = socket.gethostname()

        if self.radio == "hat":
            self.fr = farmradio.FarmRadio()
        else:
            self.fr = farmradio_usb.FarmRadio()


    def getmsg(self, timeout):
        mydata = fr.recv_raw(timeout)
    while True:
        try:
            raw_data, raw_rssi = fr.recv_raw(5.0)
    
    def recvmsg(self, msg):
        msgar = msg.split("~")
        msgts = msgar[0]
        msgto = msgar[1]
        msgfrom = msgar[2]
        msgack = msgar[3]
        msgstr = msgar[4]
        if msgto == self.myname:
            msghash = hashlib.md5(msg).hexdigest()
            if msghash in self.recv_queue 
                if msgack == 1:
                    self.sendack(msgto, msghash)
            else:
                self.recv_query[msghash] = {'from': msgfrom, 'msg': msg, 'processed': False}
                if msgack == 1:
                    send.sendack(msgto, msghash)
    #msg: ts~recp~sender~require_ack (0 or 1), msg

    # Ack a message we have recieved
    def sendack(self, msgto, msghash):
        mymsg = "ack:%s" % (msghash)
        self.sendmsg(msgt, mymsg, False)

    def sendmsg(self, msgto, base_msg, require_ack):
        curtime = int(time.time())
        if require_ack == True:
            msgack = 1
        else:
            msgack = 0
        strmsg = "%s~%s~%s~%s~%s" % (curtime, msgto, self.myname, msgack, base_msg)
        msghash = hashlib.md5(strmsg).hexdigest()
        self.send_queue[msghash] = {'to': to, 'msg': strmsg, 'sent': false, "ack": not require_ack}


if __name__ == "__main__":
    main()

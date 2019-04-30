#!/usr/bin/env python3
import time
import sys
import serial
import argparse 
import binascii 
import random
from serial.threaded import LineReader, ReaderThread

parser = argparse.ArgumentParser(description='LoRa Radio mode receiver.')
parser.add_argument('port', help="Serial port descriptor")
args = parser.parse_args()

class PrintLines(LineReader):

    def connection_made(self, transport):
        print("connection made")
        self.transport = transport
        self.send_cmd('sys get ver')
        self.send_cmd('mac pause')
        self.send_cmd('radio set mod lora')
        self.send_cmd('radio set sf sf7')
        self.send_cmd('radio set afcbw 100')
        self.send_cmd('radio set rxbw 125')
        self.send_cmd('radio set bitrate 50000')
        self.send_cmd('radio set fdev 25000')
        self.send_cmd('radio set cr 4/5')
        self.send_cmd('radio set crc off')
        self.send_cmd('radio set bw 125')
#        self.send_cmd('radio sync 12')
        self.send_cmd('radio set freq 915500000')
        self.send_cmd('radio set pwr 20')
        self.send_cmd('radio rx 0')
        self.send_cmd("sys set pindig GPIO10 0")

    def handle_line(self, data):
        if data == "ok" or data == 'busy':
            return
        if data == "radio_err":
            self.send_cmd('radio rx 0')
            return

        self.send_cmd("sys set pindig GPIO10 1", delay=0)
        if data.find("radio_rx") == 0:
            try:
                mydata = data.replace("radio_rx  FFFF0000", "")
                print(binascii.unhexlify(mydata))
            except:
                print("Bad data - Ignoring")
        else:
            print(data)
        time.sleep(.1)

        if random.randint(1,6) <= 3:
            curmsg = int(time.time())
#            print("Random Send: %s" % curmsg)
            mymsg = "%s~PIZERO3~Hey, how's it going - %s" % (curmsg, curmsg)
            mymsg = mymsg.encode("UTF-8")
            sendmsg = "radio tx " + "FFFF0000" + mymsg.hex()
            print(sendmsg)
            self.send_cmd(sendmsg)
#            self.send_cmd("radio tx %s" % hexmymsg)
            time.sleep(0.5)

        self.send_cmd("sys set pindig GPIO10 0", delay=1)
        self.send_cmd('radio rx 0')

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def send_cmd(self, cmd, delay=.5):
        self.transport.write(('%s\r\n' % cmd).encode('UTF-8'))
        time.sleep(delay)

ser = serial.Serial(args.port, baudrate=57600)
with ReaderThread(ser, PrintLines) as protocol:
    while(1):
        pass

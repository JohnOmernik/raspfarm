#!/usr/bin/python3
# Import Python System Libraries
import time
import sys
import socket
import serial
import binascii
import random

class FarmRadio():
    RADIO_FREQ_MHZ = 915.5
    RADIO_TX_PWR = 20   # The default RADIO_TX_PWR is 13, 23 is the max
    PORT = "/dev/ttyUSB0"
    TIMEOUT = 1
    myname = None
    ser = None
    prev_packet = ""
    def __init__(self):
        # Configure LoRa Radio
        print("Init - Radio")
        print("------------")
        print("Frequency: %s" % self.RADIO_FREQ_MHZ)
        print("TX Power: %s" % self.RADIO_TX_PWR)
        print("Port: %s " % self.PORT)
        print("")
        self.ser = serial.Serial(self.PORT, '57600', timeout=self.TIMEOUT)
        self.myname = socket.gethostname().lower()

        print(self.send_cmd('mac pause', 1))
        print(self.send_cmd('radio set mod lora', 1))
        print(self.send_cmd('radio set sf sf7', 1))
        print(self.send_cmd('radio set afcbw 100', 1))
        print(self.send_cmd('radio set rxbw 125', 1))
        print(self.send_cmd('radio set bitrate 50000',1))
        print(self.send_cmd('radio set fdev 25000',1))
        print(self.send_cmd('radio set cr 4/5',1))
        print(self.send_cmd('radio set crc off',1))
        print(self.send_cmd('radio set bw 125',1))
        print(self.send_cmd('radio set freq %s' % (self.RADIO_FREQ_MHZ * 1000000), 1))
        print(self.send_cmd('radio set pwr %s' % self.RADIO_TX_PWR, 1))
        print("Radio Init Complete")




    def send_cmd(self, cmd, echo=0):
        if echo == 1:
            print(cmd)
        self.ser.write(('%s\r\n' % cmd).encode('UTF-8'))
        retval = self.ser.readline().decode('UTF-8')

        retval = retval.replace("\r\n", "")
        return retval


    # check for packet rx
    def recv_raw(self, faketo):
        myto = self.TIMEOUT * 1000
#        self.send_cmd("radio set wdt %s" % myto)
        self.send_cmd('radio rx 0')
        packet = self.ser.readline()
        packet_text = ""
        data = packet.decode('UTF-8')
        if data == "radio_err":
            packet_text = "radio_err"
        elif data.find("radio_rx") == 0:
            mydata = data.replace("radio_rx  FFFF0000", "").strip()
            try:
                tpacket = binascii.unhexlify(mydata)
            except:
                print("error: %s" % mydata)
                tpacket = b"error"
            packet_text = str(tpacket, "utf-8")
            self.prev_packet = packet_text
        return packet_text


    def send_raw(self, msg):
        if len(msg) > 250: 
            print("Message to large: Not sent")
            return -1

        mymsg = msg.encode("UTF-8")
        sendmsg = "radio tx " + "FFFF0000" + mymsg.hex()
        self.send_cmd(sendmsg)
        return 0



def main():
    print ("Radio Testing")


if __name__ == "__main__":
    main()


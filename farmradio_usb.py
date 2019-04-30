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
    myname = None
    ser = None
    timeout = 2.0
    prev_packet = ""
    def __init__(self, timeout=2.0):
        # Configure LoRa Radio
        print("Init - Radio")
        print("------------")
        print("Frequency: %s" % self.RADIO_FREQ_MHZ)
        print("TX Power: %s" % self.RADIO_TX_PWR)
        print("Port: %s " % self.PORT)
        print("Packet Timeout: %s" % timeout)
        print("")
        self.timeout = timeout
        self.ser = serial.Serial(self.PORT, '57600', timeout=self.timeout)


        watchdog_timeout = int((self.timeout * 1000)) - 500
        self.myname = socket.gethostname().lower()

        print(self.send_cmd('mac pause', 1))
        time.sleep(0.1)
        print(self.send_cmd('radio set mod lora', 1))
        print(self.send_cmd('radio set freq %s' % int((self.RADIO_FREQ_MHZ * 1000000)), 1))
        print(self.send_cmd('radio set pwr %s' % self.RADIO_TX_PWR, 1))
        print(self.send_cmd('radio set sf sf7', 1))
        print(self.send_cmd('radio set afcbw 100', 1))
        print(self.send_cmd('radio set rxbw 125', 1))
        #print(self.send_cmd('radio set bitrate 125000',1))  # FSK mode only
        print(self.send_cmd('radio set fdev 5000',1))
        print(self.send_cmd('radio set prlen 8',1))
        print(self.send_cmd('radio set crc off',1))
        #print(self.send_cmd('radio set iqi off',1))
        print(self.send_cmd('radio set cr 4/5',1))
        print(self.send_cmd('radio set wdt %s' % watchdog_timeout,1))
        #print(self.send_cmd('radio set sync 12',1))
        print(self.send_cmd('radio set bw 125',1))
        print("Radio Init Complete")


    def send_cmd(self, cmd, echo=0):
        if echo == 1:
            print(cmd)
        self.ser.write(('%s\r\n' % cmd).encode('UTF-8'))
        time.sleep(0.1)
        retval = self.ser.readline().decode('UTF-8')
        retval = retval.replace("\r\n", "")
        return retval


    # check for packet rx
    def recv_raw(self):
        packet = None
        snr = None
        self.send_cmd('radio rx 0')
        packet = self.ser.readline()
        snr = self.send_cmd("radio get snr")
        packet_text = ""
        data = packet.decode('UTF-8')
        if data == "radio_err":
            packet_text = None
        elif data.find("radio_rx") == 0:
            mydata = data.replace("radio_rx  FFFF0000", "").strip()
            try:
                tpacket = binascii.unhexlify(mydata)
            except:
                print("error: %s" % mydata)
                tpacket = b"decode_error"
            packet_text = str(tpacket, "utf-8")
            self.prev_packet = packet_text
        return packet_text, snr


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


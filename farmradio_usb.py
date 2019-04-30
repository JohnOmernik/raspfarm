#!/usr/bin/python3
# Import Python System Libraries
import time
import sys
import socket
import serial
import binascii
import random

class FarmRadio():
    radio_freq_mhz = None
    radio_tx_pwr = None
    radio_serial_port = None
    radio_mode = None
    radio_spread_factor = None
    radio_crc = None
    radio_cr = None
    radio_bw = None

    timeout = None
    myname = None
    spi = None
    rfm9x = None
    ser = None
    prev_packet = None
    radio_conf={}
    debug = None

 
    def __init__(self, debug=False, timeout=2.0, radio_conf={"radio_freq_mhz": 915.5, "radio_tx_pwr": 20, "radio_serial_port": "/dev/ttyUSB0", "radio_mode": "lora", "radio_spread_factor": 7, "radio_crc": False, "radio_cr": 5, "radio_bw": 125}):

        self.debug = debug
        self.timeout = timeout
        self.radio_conf = radio_conf
        self.radio_freq_mhz = radio_conf['radio_freq_mhz']
        self.radio_tx_pwr = radio_conf['radio_tx_pwr']
        self.radio_serial_port = radio_conf['radio_serial_port']
        self.radio_mode = radio_conf['radio_mode']
        self.radio_spread_factor = str(radio_conf['radio_spread_factor'])
        self.radio_crc = bool(radio_conf['radio_crc'])
        if self.radio_crc:
            str_radio_crc = "on"
        else:
            str_radio_crc = "off"
        self.radio_cr = radio_conf['radio_cr']
        str_radio_cr = "4/%s" %  self.radio_cr
        self.radio_bw = radio_conf['radio_bw']
        # Configure LoRa Radio
        print("Init - Radio")
        print("------------")
        print("Frequency: %s" % self.radio_freq_mhz)
        print("TX Power: %s" % self.radio_tx_pwr)
        print("Port: %s " % self.radio_serial_port)
        print("Packet Timeout: %s" % timeout)
        print("")


        self.ser = serial.Serial(self.radio_serial_port, '57600', timeout=self.timeout)

        watchdog_timeout = int((self.timeout * 1000)) - 500
        self.myname = socket.gethostname().lower()
        
        print(self.send_cmd('mac pause', 1))
        time.sleep(0.1)
        print(self.send_cmd('radio set mod %s' % self.radio_mode, 1))
        print(self.send_cmd('radio set freq %s' % int((self.radio_freq_mhz * 1000000)), 1))
        print(self.send_cmd('radio set pwr %s' % self.radio_tx_pwr, 1))
        print(self.send_cmd('radio set sf sf%s' % self.radio_spread_factor, 1))
        print(self.send_cmd('radio set crc %s' % str_radio_crc,1))
        #print(self.send_cmd('radio set iqi off',1))
        print(self.send_cmd('radio set cr %s' % str_radio_cr,1))
        print(self.send_cmd('radio set wdt %s' % watchdog_timeout,1))
        #print(self.send_cmd('radio set sync 12',1))
        print(self.send_cmd('radio set bw %s' % self.radio_bw,1))
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
        elif data.find("radio_rx ") == 0:
            mydata = data.replace("radio_rx ", "").strip()
            mydata = mydata[8:]
            try:
                tpacket = binascii.unhexlify(mydata)
                packet_text = str(tpacket, "utf-8")
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


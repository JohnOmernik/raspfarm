#!/usr/bin/python3
# Import Python System Libraries
import time
import sys
import socket
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x


def main():
    print ("Radio Testing")

class FarmRadio:
    RADIO_FREQ_MHZ = 915.5
    RADIO_TX_PWR = 23   # The default RADIO_TX_PWR is 13, 23 is the max
    spi = None
    rfm9x = None
    prev_packet = None
    myname = None
    timeout = 2.0
    def __init__(self, timeout=2.0):
        # Configure LoRa Radio
        print("Init - Radio")
        print("------------")
        print("Frequency: %s" % self.RADIO_FREQ_MHZ)
        print("TX Power: %s" % self.RADIO_TX_PWR)
        print("Packet Timeout: %s" % timeout)
        print("")
        self.timeout = timeout
        self.myname = socket.gethostname().lower()
        CS = DigitalInOut(board.CE1)
        RESET = DigitalInOut(board.D25)
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, CS, RESET, self.RADIO_FREQ_MHZ)
        self.rfm9x.tx_power = self.RADIO_TX_PWR

    # check for packet rx
    def recv_raw(self):
        packet = self.rfm9x.receive(timeout=self.timeout)
        snr = None
        if packet is not None:
            self.prev_packet = packet
            snr = self.rfm9x.rssi
            try:
                packet_text = str(self.prev_packet, "utf-8")
            except:
                print("Failed Packet Decode - Dropping Packet")
                packet_text = "decode_error"
        else:
            packet_text = None
        return packet_text, snr

    def send_raw(self, msg):
        msgtime = int(time.time())
        if len(msg) > 250: 
            print("Message to large: Not sent")
            return -1
        else:
            send_data = bytes(msg, "utf-8")
            self.rfm9x.send(send_data)
            return 0


if __name__ == "__main__":
    main()


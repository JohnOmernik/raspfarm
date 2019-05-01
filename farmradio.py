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
    radio_freq_mhz = None
    radio_tx_pwr = None
    radio_serial_port = None
    radio_mode = None
    radio_spread_factor = None
    radio_crc = None
    radio_cr = None
    radio_bw = None
    radio_wdt = None

    timeout = None
    myname = None
    spi = None
    rfm9x = None
    ser = None
    prev_packet = None
    radio_conf={}
    debug = None
 
    def __init__(self, debug=False, timeout=2.0, radio_conf={"radio_freq_mhz": 915.5, "radio_tx_pwr": 20, "radio_serial_port": "spi", "radio_mode": "lora", "radio_spread_factor": 7, "radio_crc": False, "radio_cr": 5, "radio_bw": 125, "radio_wdt": 0}):
        self.debug = debug
        self.timeout = timeout
        self.radio_conf = radio_conf

        self.radio_freq_mhz = radio_conf['radio_freq_mhz']
        self.radio_tx_pwr = radio_conf['radio_tx_pwr']
        self.radio_serial_port = radio_conf['radio_serial_port']
        self.radio_mode = radio_conf['radio_mode']
        self.radio_spread_factor = radio_conf['radio_spread_factor']
        self.radio_crc = bool(radio_conf['radio_crc'])
        self.radio_wdt = radio_conf['radio_wdt']
        if self.radio_crc:
            str_radio_crc = "on"
        else:
            str_radio_crc = "off"
        self.radio_cr = radio_conf['radio_cr']
        self.radio_bw = radio_conf['radio_bw']
        # Configure LoRa Radio
        print("Init - Radio")
        print("------------")
        print("Frequency: %s" % self.radio_freq_mhz)
        print("TX Power: %s" % self.radio_tx_pwr)
        print("Port: %s " % self.radio_serial_port)
        print("Packet Timeout: %s" % timeout)
        print("")

        self.myname = socket.gethostname().lower()
        CS = DigitalInOut(board.CE1)
        RESET = DigitalInOut(board.D25)
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, CS, RESET, self.radio_freq_mhz)

        self.rfm9x.tx_power = self.radio_tx_pwr
        self.rfm9x.signal_bandwidth = self.radio_bw * 1000
        self.rfm9x.coding_rate = self.radio_cr
        self.rfm9x.spreading_factor = self.radio_spread_factor
        self.rfm9x.enable_crc = self.radio_crc

        print("Radio Init Complete")







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


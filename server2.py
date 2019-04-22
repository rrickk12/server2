#!/usr/bin/env python

from __future__ import print_function
import time
from RF24 import *
import RPi.GPIO as GPIO
from pymongo import MongoClient


radio = RF24(22,0)
pipes = ["1Node", "2Node"]


def handle_payload(payload):
    """
    Receives payload in the format "temp_value,vcc_value,serial"
    """
    client = MongoClient()
    db = client.test

    data = payload.split(",")
    data = [item.rstrip('\x00') for item in data]
    db_data = {
        "uploaded": False,
        "timestamp": int(time.time()),
        "values": {
            data[2]: data[0]
        }
    }

    db.temperatures.insert_one(db_data)

    return "OK"


def main():

    print("server.py...")
    radio.begin()
    radio.setRetries(15, 15)
    radio.printDetails()

    print("Awaiting trasmission...")
    radio.openWritingPipe(pipes[1])
    radio.openReadingPipe(1,pipes[0])
    radio.startListening()

    while 1:
        if radio.available():
            while radio.available():
                receive_payload = radio.read(32).decode('utf-8')
                print('Got payload "{}"'.format(receive_payload))

                radio.stopListening()
                radio.write("OK")
                print("Sent OK...")

                handle_payload(receive_payload)

                radio.startListening()

        time.sleep(0.2) # Roughly the timeout

    return 0            

if __name__ == "__main__":
    main()

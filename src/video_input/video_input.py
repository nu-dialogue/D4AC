#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# video_input.py
#   get camera images
# (c) Nagoya University


import cv2
import base64
import paho.mqtt.client as paho
import argparse
import os
import sys

import yaml

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from util.logger import createLogger
logger = createLogger("input video")


def on_connect(mqtt, obj, rc):
    print("connect rc:"+str(rc))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no_display", help="don't show camera image", action="store_true")
    args = parser.parse_args()

    config_file: str = os.path.join(os.path.dirname(__file__), "../config.yml")
    with open(config_file) as fp:
        config = yaml.safe_load(fp)

    mosquitto = os.environ.get('MQTT')
    if mosquitto == None:
        mosquitto = 'localhost'

    try:
        device_id: int = int(config["video_input"]["device_id"])
    except:
        logger.error("illegal device id: " + config["video_input"]["device_id"])
        sys.exit(1)
    logger.info("Using Camera " + str(device_id))
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        logger.error('video connection error')
        sys.exit(1)
    mqtt = paho.Client()
    mqtt.on_connect = on_connect
    mqtt.connect(mosquitto, 1883, 60)
    logger.info("connected mosquitto at: " + mosquitto)
    counter = 0
    try:
        while True:
            ret, frame = cap.read()
            if counter != 10:
                counter += 1
                continue
            counter = 0
            if not ret:
                break
            _, enc = cv2.imencode('.jpg', frame)
            base = base64.b64encode(enc)
            mqtt.publish("dialog/image", base)
            #logger.debug("image sent")
            if args.no_display == False:
                cv2.imshow("inputVideo", frame)
                key = cv2.waitKey(1)
                if key == 27:
                    break
    except KeyboardInterrupt:
        logger.info('interrupt')
    cap.release()
    if args.no_display == False:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

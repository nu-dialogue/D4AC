#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# d4ac_main.py
#   main module of D4AC
# (c) Nagoya University

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from util.logger import createLogger

logger = createLogger('d4ac_main')

from server import app, setConfig

import uvicorn
import yaml
import mqtt
import threading


def main():
    with open("../config.yml") as fp:
        config = yaml.safe_load(fp)
    user_status = config['user_status']
    sending_user_status = user_status['uu_end']['send'] or user_status['su_end']['send'] \
                          or user_status['silence']['send']
    if sending_user_status:
        mosquitto = os.environ.get('MQTT')
        if mosquitto is None:
            mosquitto = 'localhost'
        print('mosquitto: ' + mosquitto)
        thread = threading.Thread(target=mqtt.run, args=(mosquitto, logger))
        thread.setDaemon(True)
        thread.start()

    dialog = os.environ.get('DIALOG')
    if dialog is None:
        dialog = 'localhost'
    print('dialog: ' + dialog)
    setConfig(config, dialog, logger)

    server_port = config.get("server_port", 8000)
    uvicorn.run(app=app, host="0.0.0.0", port=server_port)


if __name__ == '__main__':
    main()

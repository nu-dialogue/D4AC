#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# logger.py
#   estimate user states from mediapipe output
# (c) Nagoya University


from logging import Formatter, StreamHandler,handlers, getLogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
import os
import sys

def createLogger(name):

    logger = getLogger(name)

    levels = {"DEBUG": DEBUG, "INFO": INFO, "WARNING": WARNING, "ERROR": ERROR, "CRITICAL": CRITICAL}
    loglevel = os.environ.get("LOGLEVEL", "DEBUG")  # default is DEBUG
    if loglevel in levels.keys():
        level = levels[loglevel]
    logger.setLevel(level)
    
    homedir = os.path.expanduser('~')
    logdir = os.path.join(homedir,'d4ac')
    os.makedirs(logdir, exist_ok = True)
    formatter = Formatter("%(asctime)s, %(process)d, %(name)s, %(levelname)s, %(message)s")
    handler = StreamHandler(stream=sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    timeHandler = handlers.TimedRotatingFileHandler(filename=logdir + "/"+name+".log", encoding="UTF-8",
                                                    when="MIDNIGHT", backupCount=30)
    timeHandler.setLevel(level)
    timeHandler.setFormatter(formatter)
    logger.addHandler(timeHandler)
    return logger

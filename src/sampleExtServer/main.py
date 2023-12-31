#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# sampleExtServer/main.py
#   sample external server (auxiliary output)
# (c) Nagoya University


#!/usr/bin/env python3
from urls import app
import uvicorn

import argparse



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=80)
    args=parser.parse_args()

    uvicorn.run(app=app, host="0.0.0.0", port=args.port)

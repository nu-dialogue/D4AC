#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# user_status_estimator.py
#   estimate user status from mediapipe output
# (c) Nagoya University

import numpy as np
import json

ring_buffer_size = 5


class UserStatusEstimator:

    def __init__(self, logger):

        self.timestamp_buffer = np.array([0.0] * ring_buffer_size)
        self.nose_end_buffer = np.array([(0.0, 0.0)] * ring_buffer_size)
        self.count = 0
        self.logger = logger

    def estimate(self, payload):

        self.logger.debug("palyload received: " + json.dumps(payload))
        timestamp = payload["timestamp"]
        nose_end = payload["rel_nose_end"]
        idx = self.count % ring_buffer_size
        self.nose_end_buffer[idx] = nose_end
        self.timestamp_buffer[idx] = timestamp

        engagement = 'low'
        if self.count < ring_buffer_size:
            result = None
        else:
            ave = np.mean(self.nose_end_buffer, axis=0)
            self.logger.debug(f"average nose end over {ring_buffer_size} frames: " + np.array2string(ave))

            if abs(ave[0]) < 0.1 and abs(ave[1]) < 0.1:
                engagement = 'high'
            elif abs(ave[0]) < 0.15  and abs(ave[1]) < 0.15:
                engagement = 'middle'
            else:
                engagement = 'low'

            result = {"engagement": str(engagement)}

        self.count += 1
        self.logger.debug("palyload to send: " + json.dumps(result))
        return result

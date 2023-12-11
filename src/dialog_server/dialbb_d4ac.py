#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# dialbb_d4ac.py
#   communicate with dialbb app
# (c) Nagoya University

import datetime
import urllib.request
import json
from util.logger import createLogger
logger = createLogger("dialbb_client")

ERROR_RESPONSE = "I'm sorry. A DialBB error has occurred."


class DialBBClient:

    def __init__(self):

        self._init_url = "http://localhost:8081/init"
        self._continue_url = "http://localhost:8081/dialogue"
        self._user_id = "d4ac"
        self._headers = {'Content-Type': 'application/json;charset=UTF-8'}
        self._session_id = ""

    def respond(self, user_input):
        """
        make response
        :param input: input from client
        :type input: json
        :return: output from dialogue server
        :rtype: json
        """
        logger.info("received: " + str(user_input))
        if user_input["initial"]:
            system_output = self._get_initial_message(user_input)
        else:
            system_output = self._reply(user_input)
        logger.info("output to d4ac: " + str(system_output))
        return system_output

    def _get_initial_message(self, input):

        data = {"user_id": self._user_id}
        logger.info("initial request to dialbb: " + str(data))
        request = urllib.request.Request(self._init_url, json.dumps(data).encode(), self._headers, method="POST")
        try:
            response = json.load(urllib.request.urlopen(request))
            logger.info("response from dialbb: " + str(response))
            self._session_id = response['session_id']
            system_utterance = response["system_utterance"]
        except Exception as e:
            raise Exception("initial request to dialbb server failed.")
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = {"systemUtterance": {"expression": system_utterance, "utterance": system_utterance},
                  "talkend": False,  # 対話の終わりかどうか
                  "sessionId": self._session_id,
                  "timestamp": time}
        return output

    def _reply(self, input):
        user_utterance = input['userUtterance']
        user_status = input["userStatus"]
        data = {"user_id": self._user_id, "session_id": self._session_id,
                "user_utterance": user_utterance, "aux_data": user_status}
        logger.info("request to dialbb: " + str(data))
        try:
            request = urllib.request.Request(self._continue_url, json.dumps(data).encode(), self._headers, method="POST")
            response = json.load(urllib.request.urlopen(request))
            logger.info("response from dialbb: " + str(response))
            system_utterance = response["system_utterance"]
            if system_utterance in ('silence', 'empty'):
                system_utterance = ''
            final = response['final']
        except Exception:
            logger.error("request failed.")
            system_utterance = ERROR_RESPONSE
            final = True
        print(f"utterance: {user_utterance}, response: {system_utterance}")
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = {"systemUtterance": {"expression": system_utterance, "utterance": system_utterance},
                  "talkend": final,  # 対話の終わりかどうか
                  "sessionId": self._session_id,
                  "timestamp": time}
        return output


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# dialog_server.py
#   sends speech recognition results and user status to a dialog server
# (c) Nagoya University

__version__ = '0.1'
__copyright__ = 'Nagoya University'


import yaml
import uvicorn
import os
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import re
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from util.logger import createLogger
from dialbb_d4ac import DialBBClient
from test_dialog import TestDialog
from dummy_dialog import DummyDialog
from sunaba_d4ac import SunabaDialog

logger = createLogger("dialog_server")

DEFAULT_PORT = 8001

user_status_requests = {}  # session id -> (keys, values) e.g. ("emotion", ["angry", "happiness"])


class Item(BaseModel):
    initial: bool
    sessionId: Optional[str] = ""
    userUtterance: Optional[str] = ""
    userStatus: Optional[dict] = {}
    timestamp: Optional[str] = ""


app = FastAPI()

request_pattern = re.compile(r"\[(.+?)\s*:\s*(.+?)\]")  # [engagement|emotion : low|angry]


@app.get('/')  # methodとendpointの指定
async def hello():
    return {"text": "hello world!"}


@app.post("/dialog/")
async def create_item(item: Item):
    logger.info("app.post /dialog/ " + str(item))

    # 対話管理からのrequestが指定されていてrequestにマッチしなければシステム発話終了時・無音時にはユーザ状態を送らない
    if item.userUtterance in ("su-end", "silence") and config['user_status']['on_request']:
        send: bool = False
        if user_status_requests.get(item.sessionId):  # 前のシステム発話にrequestがあった場合
            keys = user_status_requests[item.sessionId][0]
            values = user_status_requests[item.sessionId][1]
            if keys and values:  # user statusがある場合
                for (user_status_key, user_status_value) in item.userStatus.items():
                    if user_status_key in keys and user_status_value in values:  # requestとマッチ
                        send = True
                        break
        if not send:
            system_output = {"systemUtterance": {"expression": "", "utterance": ""},
                             "talkend": False,
                             "sessionID": item.sessionId,
                             "timestamp": 000}
            return system_output
    user_input = {"sessionId": item.sessionId, "initial": item.initial,
                  "userUtterance": item.userUtterance, "userStatus": item.userStatus,
                  "timestamp": item.timestamp}
    logger.info("sent to dialog system: " + str(user_input))
    system_output = dialog_system.respond(user_input)
    logger.info("output from dialog system: " + str(system_output))
    system_utterance = system_output["systemUtterance"]['utterance']
    system_expression = system_output["systemUtterance"]['expression']
    session_id = system_output['sessionId']

    # 対話管理からのrequestを取り出し
    m = request_pattern.search(system_utterance)
    if m:
        request = m.group(0)
        keys = m.group(1).split('|')
        values = m.group(2).split('|')
        user_status_requests[session_id] = (keys, values)
        system_output["systemUtterance"]['utterance'] = system_utterance.replace(request, "").strip()
        system_output["systemUtterance"]['expression'] = system_expression.replace(request, "").strip()
    else:
        user_status_requests[session_id] = ([], [])
    if system_output["systemUtterance"]['utterance'] in ("empty", "nomatch"):
        system_output["systemUtterance"]['utterance'] = ""
    if system_output["systemUtterance"]['expression'] in ("empty", "nomatch"):
        system_output["systemUtterance"]['expression'] = ""
    logger.info("request from dialog manager stored: " + str(user_status_requests))
    logger.info("response = " + str(system_output))
    return system_output


def main():
    f = os.path.abspath(__file__)
    dir = os.path.dirname(f)
    os.chdir(dir)
    global dialog_system
    global config
    with open("../config.yml") as fp:
        config = yaml.safe_load(fp)
    print(config)
    dialog_server = config["dialog_server"]
    server_type = dialog_server["server_type"]
    logger.info(f"server type = {server_type}")
    if server_type == "xaiml_sunaba":
        bot_id = dialog_server["botId"]
        init_topic_id = dialog_server["initTopicId"]
        dialog_system = SunabaDialog(bot_id, init_topic_id, logger)
    elif server_type == "dummy_dialog":
        dialog_system = DummyDialog()
    elif server_type == "dialbb":
        dialog_system = DialBBClient()
    elif server_type == "test_dialog":
        dialog_system = TestDialog()
    else:
        logger.error("unknown server type: " + server_type)
        raise Exception("unknown server type: " + server_type)
    port=dialog_server['port']

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    main()


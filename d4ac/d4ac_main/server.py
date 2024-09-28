from distutils.util import change_root
from controllers import *
import urllib.request
import json
import time
from mqtt import getMqttData

logger = None

url = "http://localhost:8080/dialog/"

config = {}
uu_send: bool = False
su_send: bool = False
silence_send: bool = False
gender_age_send: bool = False
only_upon_send: bool = False
post_send = False
post_url = ""


def setConfig(config_yml, host, log):
    global url
    global config
    global uu_send
    global su_send
    global silence_send

    global gender_age_send
    global only_upon_send
    global post_send
    global post_url
    global logger
    logger = log
    url = "http://" + host + ":8080/dialog/"
    config = config_yml
    print(config)
    user_status = config['user_status']
    gender_age_send = user_status['send_gender_and_age']
    uu_send = user_status['uu_end']['send']
    su_send = user_status['su_end']['send']
    silence = user_status['silence']
    silence_send = silence['send']
    only_upon_send = silence['only_upon_changes']
    post_server = config['post_server']
    post_send = post_server['enable']
    post_url = post_server['url']
    logger.info(f"uu_send = {uu_send}, su_send= {su_send}, silence = {silence}, "
                + f"post_server = {post_server}, only_upon_send = {only_upon_send}")


@app.get('/config/')
def get_config():
    return config


def post_to_dialog_server(data_to_send):
    data = json.load(data_to_send)
    try:
        headers = {'Content-Type': 'application/json'}
        request = urllib.request.Request(post_url, json.dumps(data).encode(), headers, method='POST')
        print('post req = ' + str(request))
        response = urllib.request.urlopen(request)
    except Exception():
        return {"error": "url " + url}
    return response


@app.get('/start/{utterance}')
def start(utterance: str):
    logger.info("app.get /start/"+utterance)
    timestamp = time.time()
    headers = {'Content-Type': 'application/json'}
    data = {"initial": True, "userUtterance": utterance,
            "timestamp": timestamp}
    try:
        request = urllib.request.Request(url, json.dumps(data).encode(), headers, method="POST")
        response = urllib.request.urlopen(request)
    except Exception():
        return {"error": "url: " + url}
    if post_send:
        response = post_to_dialog_server(response)
    system = json.load(response)

    logger.info("response =" + str(system))
    return system


@app.get('/continue/{sessionid}/')  # no asr_result
def process_no_asr_result(sessionid: str):
    return process(sessionid, "")


@app.get('/continue/{sessionid}/{utterance}')
def process(sessionid: str, utterance: str):
    logger.info("app.get /continue/"+sessionid + "/" + utterance)
    timestamp = time.time()
    headers = {'Content-Type': 'application/json'}
    
    if uu_send:
        user_status = getMqttData(False, gender_age_send, logger)
        if user_status['changed']:
            data = {"initial": False, "userUtterance": utterance, "sessionId": sessionid,
                    "userStatus": user_status['userstatus'], "timestamp": timestamp}
        else:
            data = {"initial": False, "userUtterance": utterance, "sessionId": sessionid,
                    "timestamp": timestamp}
        logger.info(f"data = {data}")
    else:
        data = {"initial": False, "sessionId": sessionid, "userUtterance": utterance, "timestamp": timestamp}
    logger.info("send data -> "+str(data))
    try:
        request = urllib.request.Request(url, json.dumps(data).encode(), headers, method="POST")
        response = urllib.request.urlopen(request)
    except Exception():
        return {"error": "url: " + url}
    if post_send:
        response = post_to_dialog_server(response)
    system = json.load(response)
    logger.info("response =" + str(system))
    return system


@app.get('/continuefirst/{sessionid}/{utterance}')  # first user utterance
def process_first_utterance(sessionid: str, utterance: str):
    return process(sessionid, utterance)


@app.get('/continuefirst/{sessionid}/')  # first user utterance
def process_first_utterance_without_no_asr_result(sessionid: str):
    return process(sessionid, "")


@app.get('/engagement/{sessionid}')
def engagement(sessionid: str):
    logger.info("app.get /engagement/" + sessionid )
    timestamp = time.time()
    if su_send == True:
        headers = {'Content-Type': 'application/json'}
        userstatus = getMqttData(False, False, logger)
        if userstatus['changed']:
            data = {"initial": False, "userUtterance": 'su-end', "sessionId": sessionid,
                    "userStatus": userstatus['userstatus'], "timestamp": timestamp}
            logger.info(f"data = {data}")
            try:
                request = urllib.request.Request(url, json.dumps(data).encode(), headers, method="POST")
                response = urllib.request.urlopen(request)
            except Exception():
                return {"error": "url " + url}
            if post_send:
                response = post_to_dialog_server(response)
            system = json.load(response)
            logger.info("response = " + str(system))
            return system
        else:
            return {"status": "nothing changed"}


@app.get('/userstatus/{sessionid}')
def userstatus(sessionid:str):
    logger.info("app.get /userstatus/" + sessionid )
    timestamp = time.time()
    if silence_send  == True:
        headers = {'Content-Type': 'application/json'}
        userstatus = getMqttData(only_upon_send, gender_age_send, logger)
        if userstatus['changed']:
            data = {"initial": False, "sessionId": sessionid, 'userUtterance': 'silence',
                    "userStatus": userstatus['userstatus'], "timestamp": timestamp}
            logger.info(f"data = {data}")
            try:
                request = urllib.request.Request(url, json.dumps(data).encode(), headers, method="POST")
                response = urllib.request.urlopen(request)
            except Exception():
                return {"error": "url "+ url}
            if post_send:
                response = post_to_dialog_server(response)
            system = json.load(response)
            logger.info("response = "+ str(system))
        else:
            system = {"status": "nothing changed"}
            logger.info(f"userstatus is not changed------ do not send server ")
        return system


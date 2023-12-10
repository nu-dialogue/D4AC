import paho.mqtt.client as paho
import time
import json

engagement = ""
emotion = ""
gender = ""
age = 0

old_emotion = ""
old_engagement = ""
received = False


def getMqttData(send_only_changed, gender_age, logger=None):
    global old_emotion
    global old_engagement
    global received
    if not received:
        new_engagement = 'low'
        new_emotion = old_emotion
    elif send_only_changed:

        if old_emotion == emotion:
            new_emotion = ""
        else:
            new_emotion = emotion
            old_emotion = emotion
        if old_engagement == engagement:
            new_engagement = ""
        else:
            new_engagement = engagement
            old_engagement = engagement
        
    else:
        new_emotion = emotion
        old_emotion = new_emotion
        new_engagement = engagement
        old_engagement = new_engagement
    received = False
    user_status = {"engagement": new_engagement,'emotion': new_emotion,}
    if gender_age:
        if age > 59:
            new_age = 'senior'
        elif age > 35:
            new_age = 'middle'
        elif age > 19:
            new_age = 'young'
        elif age > 12:
            new_age = 'teenager'
        elif age > 0:
            new_age = 'child'
        else:
            new_age = 'unknown'
        
        user_status['age'] = new_age
        user_status['gender'] = gender

    elif new_emotion == "" and new_engagement == "":
        logger.info("**** changed false ****")
        return {"changed":False}
    if logger is not None:
        logger.info(f"status = {user_status}, send_only_changed = {send_only_changed}, gender_age = {gender_age}")
    return {"userstatus": user_status, "changed": True}


def on_connect(client, userdata, flag, rc):
    print("connected result code " + str(rc))
    client.subscribe("dialog/user_status")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


def on_message(client, userdata, msg):
    global engagement
    global emotion
    global gender
    global age
    global received
    payload = json.loads(msg.payload)
    print("payload = " + str(payload))
    user_status = payload["user_status"]
    engagement = user_status.get('engagement', '')
    emotion = user_status.get('emotion', '')
    gender = user_status.get('gender', '')
    age = user_status.get('age', 0)
    received = True


def run(mosquitto,logger):
    # MQTTの接続設定
    client = paho.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    logger.info("MQTT client start")
    client.connect(mosquitto, 1883, 60)
    client.loop_forever()

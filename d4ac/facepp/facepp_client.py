#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# faceapp_client.py
#   client of face++
# (c) Nagoya University


import json
import requests
import paho.mqtt.client as paho
import os
import time
import traceback
import sys
import yaml


sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
from util.logger import createLogger
logger = createLogger("facepp_user_status")

config = None


def on_connect(client, userdata, flag, rc):
    try:
        client.subscribe("dialog/image")
    except Exception as e:
        t = list(traceback.TracebackException.from_exception(e).format())
        logger.error("on_connect_error " + str(t))


def on_disconnect(client, userdata,  rc):
    if rc != 0:
        logger.error("unexpected disconnection")


def on_message(client, userdata, msg):

    global count
    count = count + 1
    if count > 5:
        count = 0
        try:
            print("topic '" + msg.topic + "' QoS " + str(msg.qos))
            data = {'api_key': config['facepp']['apikey'],
                    'api_secret': config['facepp']['secret'],
                    'image_base64': msg.payload,
                    'return_landmark': 1,
                    'return_attributes': 'gender,age,headpose,emotion'
            }

            #print(msg.payload)
            print("api_key: " + config['facepp']['apikey'])

            req = requests.post('https://api-us.faceplusplus.com/facepp/v3/detect', data=data)
            response = req.json()

            logger.debug("response from facepp: " + str(response))
            faces = response['faces']

            # access the response, example:
            for face in faces:
                print('Facial attributes detected:')
                attributes = face['attributes']
                age = attributes.get('age','').get('value','')
                print('Age: ', age)
                gender = attributes['gender']['value']
                print('Gender: ', gender)
                emotion = attributes['emotion']
                print('Emotion: ')
                print('\tAnger: ', emotion['anger'])
                print('\tDisgust: ', emotion['disgust'])
                print('\tFear: ', emotion['fear'])
                print('\tHappiness: ', emotion['happiness'])
                print('\tNeutral: ', emotion['neutral'])
                print('\tSadness: ', emotion['sadness'])
                print('\tSurprise: ', emotion['surprise'])
                print()
                headpose = attributes['headpose']
                roll = headpose['roll_angle']
                yaw = headpose['yaw_angle']
                pitch = headpose['pitch_angle']
                if abs(roll) < 15 and abs(yaw) < 15 and abs(pitch) < 15:
                    engagement = "high"
                elif abs(roll) < 25 and abs(yaw) < 25 and abs(pitch) < 25:
                    engagement = "middle"
                else:
                    engagement = "low"
                sorting = [{"name": "anger", "value": emotion['anger']},
                           {"name": "disgust", "value": emotion['disgust']},
                           {"name": "fear", "value": emotion['fear']},
                           {"name": "happiness", "value": emotion['happiness']},
                           {"name": "neutral", "value": emotion['neutral']},
                           {"name": "sadness", "value": emotion['sadness']},
                           {"name": "surprise", "value": emotion['surprise']}]
                so = sorted(sorting, key=lambda i: i['value'], reverse=True)
                
                emotion = so[0]['name']
                logger.info(f"emotion = {emotion}, value = {str(so[0]['value'])}, engagement = {engagement}, "
                            + f"roll = {str(roll)}, yaw = {str(yaw)}, pitch = {str(pitch)}")
                result = {"engagement": str(engagement), "emotion": emotion, 'gender': gender, 'age': age}
                payload_to_send = {"timestamp": time.time(), "user_status": result}
                logger.info(f'send --> {payload_to_send}')
                msg_to_send = json.dumps(payload_to_send)
                client.publish("dialog/user_status", msg_to_send)
        except Exception as e:
            t = list(traceback.TracebackException.from_exception(e).format())
            logger.error("on_message_error" + str(t))


def main():

    global config
    
    f = os.path.abspath(__file__)
    dir = os.path.dirname(f)
    os.chdir(dir)   

    with open("../config.yml") as fp:
        config = yaml.safe_load(fp)

    mosquitto = os.environ.get('MQTT')
    if mosquitto is None:
        mosquitto = 'localhost'

    global count
    count = 0

    # MQTTの接続設定
    client = paho.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(mosquitto, 1883, 60)
    logger.info("connected mosquitto at: " + mosquitto)
    client.loop_forever()
    # client.loop_stop()


if __name__ == '__main__':
    main()

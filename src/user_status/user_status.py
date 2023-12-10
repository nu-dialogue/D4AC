import json
import paho.mqtt.client as paho
import os
import traceback
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from util.logger import createLogger
logger = createLogger("user_status")
from user_status_estimator import UserStatusEstimator


def on_connect(client, userdata, flag, rc):
    try:
        client.subscribe("dialog/face_direction")
    except Exception as e:
        t = list(traceback.TracebackException.from_exception(e).format())
        logger.error("on_connect_error " + str(t))


def on_disconnect(client, userdata,  rc):
    if rc != 0:
        logger.error("unexpected disconnection")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload)
        user_status = user_status_estimator.estimate(payload)
        if user_status is not None:
            payload_to_send = {"timestamp": payload["timestamp"], "user_status": user_status}
            msg_to_send = json.dumps(payload_to_send)
            client.publish("dialog/user_status", msg_to_send)
    except Exception as e:
        t = list(traceback.TracebackException.from_exception(e).format())
        logger.error("on_message_error" + str(t))


if __name__ == '__main__':

    user_status_estimator = UserStatusEstimator(logger)
    mosquitto = os.environ.get('MQTT')
    if mosquitto is None:
        mosquitto = 'localhost'

    # MQTTの接続設定
    client = paho.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(mosquitto, 1883, 60)
    logger.info("connected mosquitto at: " + mosquitto)
    client.loop_forever()
    # client.loop_stop()

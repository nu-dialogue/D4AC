#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# mesh.py
#   mediapipe client
# (c) Nagoya University


import mediapipe as mp
import paho.mqtt.client as paho
import sys
import traceback
import base64
import os
import numpy as np
import cv2
import time
import json

mp_face_mesh = mp.solutions.face_mesh

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from util.logger import createLogger
logger = createLogger("mediapipe")

image_points = np.array([
    (359, 391),     # Nose tip 30
    (399, 561),     # Chin 8
    (337, 297),     # Left eye left corner 36
    (513, 301),     # Right eye right corner 45
    (345, 465),     # Left Mouth corner 48
    (453, 469)      # Right mouth corner 54
], dtype="double")

model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corne
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
])


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

    img = base64.b64decode(msg.payload)
    jpg = np.frombuffer(img,dtype=np.uint8)
    with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True) as face_mesh:
        img2 = cv2.imdecode(jpg, flags=cv2.IMREAD_COLOR)
        height, width, _ = img2.shape
        results = face_mesh.process(cv2.cvtColor(img2,cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return
        for face_landmarks in results.multi_face_landmarks:
                
            landmark = face_landmarks.landmark
            lefteye = (int(landmark[33].x * width), int(landmark[33].y * height))
            righteye = (int(landmark[263].x * width), int(landmark[263].y * height))
            nose = (int(landmark[1].x * width), int(landmark[1].y * height))
            leftmouse = (int(landmark[76].x * width), int(landmark[76].y * height))
            rightmouse = (int(landmark[306].x * width), int(landmark[306].y * height))
            chin = (int(landmark[152].x * width), int(landmark[152].y * height))
            size = img2.shape
            focal_length = size[1]
            center = (size[1]/2, size[0]/2)
            camera_matrix = np.array(
                [[focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]], dtype="double"
            )
            image_points = np.array([nose, chin, lefteye, righteye, leftmouse, rightmouse], dtype="double")
            dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
            (success, rotation_vector, translation_vector) \
            = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

            (nose_end_point2D, jacobian) = cv2.projectPoints(np.array(
                [(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)

            for p in image_points:

                p1 = (int(image_points[0][0]), int(image_points[0][1]))
                p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
                rel_nose_end_point=((p2[0]-p1[0])/size[0], (p2[1]-p1[1])/size[1])

#                cv2.line(img2, p1, p2, (255, 0, 0), 2)
#                if rel_nose_end_point[0] > 1.0 or  rel_nose_end_point[1] > 1.0:
#                    cv2.circle(img2, (p2[0], p2[1]), 5, (255, 255, 0), -1)
#                if rel_nose_end_point[0] < -1.0 or  rel_nose_end_point[1] < -1.0:
#                    cv2.circle(img2, (p2[0], p2[1]), 5, (0, 255, 255), -1)
                rotation_vector_list = rotation_vector.tolist()
                translation_vector_list = translation_vector.tolist()
                timestamp = time.time()
                logger.debug(f"nose_end {rel_nose_end_point[0]}, {rel_nose_end_point[1]}")
                payload = {"timestamp": timestamp, "rotation": rotation_vector_list,
                   "translation": translation_vector_list, "rel_nose_end": rel_nose_end_point}
                msg_to_send = json.dumps(payload)
                if success:
                    client.publish("dialog/face_direction", msg_to_send)
                    #logger.debug("payload sent: " + msg_to_send)#print(str(payload), file=fp)
#                cv2.imshow("debug",img2)
#                cv2.waitKey(0)



def main():

    mosquitto = os.environ.get('MQTT')
    if mosquitto == None:
        mosquitto = 'localhost'
    #print('mosquitto: ' + mosquitto)
    
    # MQTTの接続設定
    client = paho.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(mosquitto, 1883, 60)
    logger.info("connected mosquitto at: " + mosquitto)
    client.loop_forever()
    return 0


if __name__ == '__main__':
    main()
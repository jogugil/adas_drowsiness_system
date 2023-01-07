Librerias utilizadas:

%matplotlib inline 
from matplotlib import pyplot as plt

import os
import cv2
import dlib
import time
import json
import serial
import random
import imutils
import logging
import argparse
import keyboard
import datetime
import platform
import threading
import numpy as np 
import tkinter as  tk
import multiprocessing
import paho.mqtt.client as paho


from paho import mqtt

from time import sleep
from time import perf_counter

from sinfo import sinfo
from threading import Thread

from tkinter import *
from tkinter import  font,ttk

from matplotlib import pyplot

from pynq.lib.video import *

from imutils import face_utils
from imutils.video import VideoStream
from imutils.video import FileVideoStream

from IPython.display import clear_output
from scipy.spatial import distance as dist
 

 --------------------
 
 Entorno:
 
 ![image](https://user-images.githubusercontent.com/15160072/211155563-dd644342-3e27-4474-8752-eccdbb2c2018.png)

 
* PYNQ-Z2 V3.1: https://pynq.readthedocs.io/en/latest/getting_started/pynq_z2_setup.html
* Python 3.9: https://www.python.org/downloads/release/python-390/
* HiveMQ: https://www.hivemq.com/
* Paho Python: https://pypi.org/project/paho-mqtt/


--------------
import iotadas as adas ----- (desarrollado en el proyecto)


Para que funcione es necesario unos subdirectorios donde se tenga  la red preentrenada y los modelos entrenados.  Además, en pcsystem debemos tener un conjunto de subdirectorios  donde se almcenaran los usurios registrados.
Aunque no se usan todos los modelos almacenados en ficheros xml, si los tendrémos para posteriores desarrollos.

La primera vez tendras que regstrarte desde el Front-End de PC-System.

En PC-System:


\sin_com_uart\
               - iotadas.py
               - Login_App_onlyMQTT.ipynb
               - \data\
                        - \reconocimiento
                        -  \users
                - \model\
                         -  upper_body2.xml"
                            eye.xml"
                            face.xml"
                            face_cv2.xml"
                            face2.xml"
                            face3.xml"
                            face4.xml"
                            fullbody.xml"
                            glasses.xml"
                            haarcascade_car.xml"
                            haarcascade_eye.xml"
                            haarcascade_frontalface_alt2.xml"
                            haarcascade_frontalface_default.xml" (**)
                            haarcascade_fullbody.xml"
                            lbpcascade_frontalface.xml"
                            left_ear.xml"
                            left_eye2.xml"
                            lefteye.xml"
                            lower_body.xml"
                            mouth.xml"
                            nose.xml"
                            profile.xml"
                            right_ear.xml"
                            right_eye.xml"
                            right_eye2.xml"
                            shape_predictor_68_face_landmarks.dat" (**)
                            two_eyes_big.xml"
                            two_eyes_small.xml"
                            upper_body.xml"
                         |
                         \users\

En PYNQ-SYSTEMS:


    APP_IOT_MQTT_ONLY_PROD.ipynb
    \data
         |
         \reconocimiento
         |
         \users

    \model\
           -  upper_body2.xml"
              eye.xml"
              face.xml"
              face_cv2.xml"
              face2.xml"
              face3.xml"
              face4.xml"
              fullbody.xml"
              glasses.xml"
              haarcascade_car.xml"
              haarcascade_eye.xml"
              haarcascade_frontalface_alt2.xml"
              haarcascade_frontalface_default.xml"
              haarcascade_fullbody.xml"
              lbpcascade_frontalface.xml"
              left_ear.xml"
              left_eye2.xml"
              lefteye.xml"
              lower_body.xml"
              mouth.xml"
              nose.xml"
              profile.xml"
              right_ear.xml"
              right_eye.xml"
              right_eye2.xml"
              shape_predictor_68_face_landmarks.dat" (**)
              two_eyes_big.xml"
              two_eyes_small.xml"
              upper_body.xml"
           |
           \users\

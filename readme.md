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
* dlib: http://dlib.net/
https://unipython.com/instalar-dlib/

* oepncv-python: https://opencv.org/opencv-face-recognition/

---
import iotadas as adas ----- (desarrollado en el proyecto)


Para que funcione es necesario unos subdirectorios donde se tenga  la red preentrenada y los modelos entrenados.  Además, en pcsystem debemos tener un conjunto de subdirectorios  donde se almcenaran los usurios registrados.
Aunque no se usan todos los modelos almacenados en ficheros xml, si los tendrémos para posteriores desarrollos.

La primera vez tendras que regstrarte desde el Front-End de PC-System.

En PC-System:




\sin_com_uart\
     
     Login_App_onlyMQTT.ipynb
     
     iotadas.py
     
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
           
 (**) shape_predictor_68_face_landmarks.dat . Se necesita buscarlo por internet y descrgarlo, colocandolo en el subdirectorio model         
 Artículos interesantes:
 
 - https://www.researchgate.net/publication/264419855_One_Millisecond_Face_Alignment_with_an_Ensemble_of_Regression_Trees
 - https://learnopencv.com/introduction-to-mediapipe/
 - https://github.com/dsuess/mediapipe-pytorch
 
 
 Arranque rápido:
 
 	Entorno 1 
 
o	PC: 
      	Módulo ioadas.py
      	Notebook: Login_App_onlyMQTT.ipynb
      	Subdirectorios:
              •	./data/users
              •	./data/reconocimientos
              •	./model/shape_predictor_68_face_landmarks.dat
              •	./model/ *.xml
              •	./model/user
o	PYNQ:
        	Notebook: APP_IOT_MQTT_ONLY_PROD.ypnib
PASOS:
      1.	Vas a la PYNQ y ejecutas todos los chuncks del notebook APP_IOT_MQTT_ONLY_PROD.ypnib. 
      2.	En dicho notebook se ejecuta : init_app () # Sin control de somnolencia en la pynq
      3.	Vas al PC y ejecutas : Login_App_onlyMQTT.ipynb
                Nota: Debes registrarte antes

	Entorno 2 . NO RECOMENDABLE
o	PC: 
     	Módulo ioadas.py
     	Notebook: Login_App_onlyMQTT.ipynb
     	Subdirectorios:
                  •	./data/users
                  •	./data/reconocimientos
                  •	./model/shape_predictor_68_face_landmarks.dat
                  •	./model/ *.xml
                  •	./model/user
o	PYNQ:
     	Notebook: APP_IOT_MQTT_ONLY_PROD.ypnib

PASOS:
       1.	Vaya a PC-System y en la función   init_app () del fichero de PC-system Login_App.ipynb y comentar:
           event = multiprocessing.Event() 
           r_somno = threading.Thread(target = adas.run_drowsiness,args=(event,))
           r_somno.start ()

       2.	Vas a la pynq y ejecutas los cucks APP_IOT_MQTT_ONLY_PROD.ypnib : init_app_con_somnolencia ()  
       3.	Vas al PC y ejecutas : Login_App_onlyMQTT.ipynb
              Nota: Debes registrarte antes
              
              
	Entorno 3 . 
o	PC: 
        	Módulo ioadas.py
        	Notebook: Login_App.ipynb
        	Subdirectorios:
                •	./data/users
                •	./data/reconocimientos
                •	./model/shape_predictor_68_face_landmarks.dat
                •	./model/ *.xml
                •	./model/user
o	PYNQ:
        	Notebook: APP_IOT_UART_PROD.ypnib

PASOS:
        1.	Vas a la PYNQ y ejecutas todos los chucks del notebook APP_IOT_UART_PROD.ypnib. 
        2.	En dicho notebook se ejecuta : init_app () # Sin controlo de somnolencia en la pynq
        3.	Vas al PC y ejecutas : Login_App.ipynb
             Nota: Debes registrarte antes

	Entorno4 . NO RECOMENDABLE
o	PC: 
          	Módulo ioadas.py
          	Notebook: Login_App.ipynb
          	Subdirectorios:
                     •	./data/users
                     •	./data/reconocimientos
                     •	./model/shape_predictor_68_face_landmarks.dat
                     •	./model/ *.xml
                     •	./model/user
o	PYNQ:
           	Notebook: APP_IOT_UART_PROD.ypnib

PASOS:
         1.	Vas a la PYNQ y en el notebook APP_IOT_PROD.ypnib.  comentas las líneas de código:
           event = multiprocessing.Event() 
             r_somno = threading.Thread(target = adas.run_drowsiness,args=(event,))
             r_somno.start ()
           presente en la función init_app ()
         2.	Vas a la pynq y ejecutas los cucks APP_IOT_UART_PROD.ypnib : init_app_con_somnolencia ()  
         3.	Vas al PC y ejecutas : Login_App.ipynb
             NOTA: Debes registrarte antes

Si quieres probas sólo el control somnolencia:
-	PC: Puedes lanzar el noteboock : Login_App_onlyMQTT.ipynb sin lanzar el script de PYNQ. (los mensajes se almacenarán en HiceMQ sin consumirse). Luego puedes jugar con el módulo.
-	PYNQ: Puedes ejecutar y probar cualquiera de los módulos por separado. después de la implementación del módulo se ha dejado un Chuck para probarlos. 


Nota: En los entornos 3 y 4 que se utiliza bluetooth hay que configurar el puerto COM? del PC donde se ejecute.

**INTEGRAR DLIB en la PYNQZ2 unbuntu 24.04, Python 3.10, onnx y sin tener cuda**
(Disponer una SD de almenos 64G)


    1. Crearte 10 G de swap para poder tener en la compleción.
    
     1.a) 
     
            sudo su
            
            apt-get update && apt-get upgrade
            
            shutdown -r now
            
     1.b) 
     
           sudo su
           
           cd /
           
           dd if=/dev/zero of=swapfile bs=1M count=10000
           
           mkswap swapfile
           
           swapon swapfile
           

         1.c)
                  nano /etc/fstab   /swapfile none swap sw 0 0
         1.d)
                  swapoff -v /var/swap
                  rm -R /var/swap
         1.5)
                 swapon -s
                 shutdown -r now
          1.6)
                 sudo su
                 chmod 600 /swapfile

    2. 2)	Compilar e integrar ‘dlib’
            cd ~
                 mkdir temp
            cd temp
                  git clone https://github.com/davisking/dlib.git
            cd dlib
                  mkdir build; cd build; cmake ..; cmake --build .
            cd ..
                   python3 setup.py install

    
    
    

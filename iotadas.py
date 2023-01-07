import time
import json
import serial
import logging
import keyboard
import datetime
import threading
from paho import mqtt
from time import sleep
from sinfo import sinfo
from threading import Thread
from time import perf_counter
import paho.mqtt.client as paho
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import multiprocessing
import numpy as np # Biblioteca de procesamiento de datos numpy
import argparse
import imutils
import time
import dlib
import cv2



# Definición del logger root
# -----------------------------------------------------------------------------
logging.basicConfig(
    format = '%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s',
    level  = logging.INFO,
    filemode = "a"
    )
# Nuevos handlers
# -----------------------------------------------------------------------------
# Si el root logger ya tiene handlers, se eliminan antes de añadir los nuevos.
# Esto es importante para que los logs no empiezen a duplicarse.
if logging.getLogger('').hasHandlers():
    logging.getLogger('').handlers.clear()
    
# Se añaden tres nuevos handlers al root logger, uno para los niveles de debug o
# superiores, otro recogida de datos y otro para que se muestre por pantalla los niveles de info o
# superiores.

log_data= f"logs_data_{datetime.datetime.now().strftime('%Y%m%d.log')}"
file_data_handler = logging.FileHandler(log_data)
 
file_data_handler.setLevel(logging.CRITICAL)
file_data_format = logging.Formatter('%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s')
file_data_handler.setFormatter(file_data_format)
logging.getLogger('').addHandler(file_data_handler)

log_debg = f"logs_debug_{datetime.datetime.now().strftime('%Y%m%d_test.log')}"
file_debug_handler = logging.FileHandler(log_debg)
#file_debug_handler .TimedRotatingFileHandler(filename = log_debg,  when='s', interval=1, backupCount=5)
 
file_debug_handler.setLevel(logging.DEBUG)
file_debug_format = logging.Formatter('%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s')
file_debug_handler.setFormatter(file_debug_format)
logging.getLogger('').addHandler(file_debug_handler)

consola_handler = logging.StreamHandler()
consola_handler.setLevel(logging.INFO)
consola_handler_format = logging.Formatter('%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s')
consola_handler.setFormatter(consola_handler_format)
logging.getLogger('').addHandler(consola_handler)     

# Definición Constantes y Mensajes Intercambio HiveMQtt e UART/Bluetooth
#----------------------------------------------------------------
RGBLEDS_XGPIO_OFFSET = 0
RGBLEDS_START_INDEX  = 4
RGB_CLEAR    = 0
RGB_BLUE     = 1
RGB_GREEN    = 2
RGB_CYAN     = 3
RGB_RED      = 4
RGB_MAGENTA  = 5
RGB_YELLOW   = 6
RGB_WHITE    = 7
MAX_LEDS_RGB = 2

rgbled_position = [4,5]
PORT_UART   ="COM5"
BAUD_SERIAL = 9600

Delay0 = 1.8
Delay1 = 0.3
Delay2 = 0.1
 
host          ="dbd25372b1b647e895c3f4adb0260f4e.s2.eu.hivemq.cloud" 
port          = 8883
clean_session = True
client_id     = "Client_00"
server_id     = "Client_01"
client_cam_id = "Client_02"

user_name     = "adasjg01"
password      = "adas2022_01"

user_name2     = "adasjg01"
password2      = "adasjg02_iot02"

user_name_cam     = "adasjg_cam"
password_cam      = "adas2022_cam"
#De esta manera puedo leer los mensajes que llegan al topic 'ADASJG01/Server/'
# y subcarpetas 'ADASJG01/Server/cam/',...

topic_sub_server      = "ADASJG01/Server/#" 
topic_pub_server      = "ADASJG01/Pynq/"
topic_pub_client_cam  = "ADASJG01/Pynq/cam"

MSG_LOGIN              = '{"clientid":"AGASDJG01","action":"DTC","event":"LOGIN","status":"OK"}'

MSG_DTC_JSON           = '{"clientid":"AGASDJG01","action":"DTC","event":"None"}'


MDG_RTC_JSON_BUZZER    =  '{"clientid":"AGASDJG01","action":"RTC", \
                             "event":"BUZZER","paramms":["a,b,c,d,e,f,g,A",\
                                                         "1, 1, 1, 1, 1, 1, 2, 1",\
                                                          "10","3"]}'
MDG_RTC_JSON_SERVO     =  '{"clientid":"AGASDJG01","action":"RTC", \
                             "event":"SERVO","paramms":["180"]}'

MDG_RTC_JSON_LED_STICK =  '{"clientid":"AGASDJG01","action":"RTC", \
                             "event":"LED_STICK","paramms":["0xFF00FF"]}' 

MSG_DTC_TEMP = '{"clientid":"AGASDJG01","action":"DTC","event":"DTTEMP","Temp":"23"}'
MSG_RTC_TEMP = '{"clientid":"AGASDJG01","action":"RTC","event":"DTTEMP","Temp":"23"}'

MSG_DTC_LIGHT_INT = '{"clientid":"AGASDJG01","action":"DTC","event":"DTLIGTH","ILight":"23.2"}'
MSG_RTC_LIGHT_INT = '{"clientid":"AGASDJG01","action":"RTC","event":"DTLIGTH","ILight":"23.2"}'

"""
'DROWSINESS'  - detección de somnolencia (cam)
'DTBLINK'     - detección parpadeo (cam)
'DTYAWN'      - detección bostezo  (cam)
'DTSMOKING'   - detección fumando  (cam)
'DTDRINK'     - detección bebiendo (cam)
'DTEATING'    - detección comiendo (cam)
'DTMOBL'      - detección movil    (cam)
'DTLIGTH'     - detección de luz interna  (sensor intensidad de luz)
'DTTEMP'      - detección temperatura     (sensor temperatura interna)
'DANGPOS'     - no se detecta a cara del conductor, bien por taparse o posición inadecuada
--------
'BUZZER'    - Creación sonido alarma
'LED_STICK' - Señalizacion mediante testigos de luz
'SERVO'     - Movimiento SERVO, simulando conducción autónoma
"""

EVENT_LOGIN     = "LOGIN"
EVENT_NFTR      = "NFTR" # Sin implementar
EVENT_DANGPOS   = "DANGPOS"  
#-- sensor Cam
EVENT_DROWSINESS = 'DROWSINESS'
EVENT_DTBLINK    = "DTBLINK"
EVENT_DTYAWN     = "DTYAWN"
EVENT_DTSMOKING  = "DTSMOKING"
EVENT_DTDRINK    = "DTDRINK"
EVENT_DTEATING   = "DTEATING"
EVENT_DTMOBIL    = 'DTMOBIL'
#-- Sensor Temp
EVENT_DTTEMP     = "DTTEMP"
#-- Sensor Intensidad de Luz
EVENT_DTLIGTH    = "DTLIGTH"

#--- Actuadores
EVENT_BUZZER    = "BUZZER"
EVENT_LED_STICK = "LED_STICK"
EVENT_SERVO     = "SERVO" 
  
 
   
# MQTT
#--------------------------------------------------------

# Publicador eventos CAM
#------------------------------------------------------------


def on_connect_client_cam (client, userdata, flags, rc, properties=None):
 
    print("CLient_Cam::>>> CONNACK received with code %s." % rc)
    print ("CLient_Cam::>>> Connect %s result is: %s" % (host, rc))
    if rc == 0:
        client.connected_flag = True
        print ("CLient_Cam::>>> Connected OK")
        return
     
    print ("CLient_Cam::>>> Failed to connect")
    print(rc)
    
# with this callback you can see if your publish was successful
def on_publish_client_cam (client, userdata, mid, properties=None):
    print("CLient_Cam ::>>> mid: " + str(mid))
  
def connect_client_cam ():
 """
  Conecta topic 'ADASJG01/Pynq/cam'
  aunque con implementar una función de conexión sobraría (pasando como parametro el client_id)
  vamos a implementar dos funciones por separado para identificar claramente los dos clientes 
  que se tienen sobre el mismo broker mqtt
 """
 global client_cam
 global sem_client #Sabemos que connect_client_cam () sólo se ejecuta una única vez
 
 sem_client = threading.Semaphore()  # Para publicar mesajes mediante diferentes hilos en exclusión y con sección critica (la publicación)
 
 # using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
 # userdata is user defined data of any type, updated by user_data_set()
 # client_id is the given name of the client
 client_cam = paho.Client (client_id=client_cam_id, userdata=None, protocol=paho.MQTTv5)
 client_cam.on_connect = on_connect_client_cam
 # enable TLS for secure connection
 client_cam.tls_set (tls_version=mqtt.client.ssl.PROTOCOL_TLS)
 # set username and password
 client_cam.username_pw_set (user_name_cam, password_cam)
 # connect to HiveMQ Cloud on port 8883 (default for MQTT)
 print(host)
 print(port)
 client_cam.connect (host, port, keepalive = 60)
 client_cam.connected_flag = False
 while not client_cam.connected_flag: #wait in loop
     client_cam.loop()#client_cam.loop_start()
     sleep (1)
     print("NO CONECTA")
 
 
 
 
def disconnect_client_cam():
    logging.info("disconnect_client_cam")
    if 'client_cam' in globals():
        client_cam.connected_flag = False
        client_cam.disconnect  ()
        client_cam.unsubscribe(topic_pub_client_cam)
        client_cam.loop_stop ()
#------------
# send_cloud_cam_mseg (topic,msg_out): Envia los eventos de parpadeo/bostezo/Somnolencia a la pynq
# Realement eenvia las accciones que debe realiar ante dichas situaciones.
# Al igual que con la función de conexión. Vamos a crear dos funciones de publicación por cliente (hilo)
# realmente con una sóla implementación sobraría (pasas como parametro la instancia de tu cliente)
#---------------
def send_cloud_cam_mseg (msg_out):
    sem_client.acquire()
 
    #Sección crítica, par aevitar problemas de multithreding a la hora de enviar notficaciones
    #por eventos de somnolencia
    logging.info("send_cloud_cam_mseg")
    topic = topic_pub_client_cam # Debería ser por fichero de configuración
 
    if msg_out is not None and len (msg_out) > 0:
        for i in range(0,len(msg_out)):
            msg = msg_out [i]
            client_cam.publish (topic, payload = msg, qos=0)
       
       
    sem_client.release()  
       
#--------------------------------------------------------------------
#Publicador/Subcritor Eventos PYNQ
#------------------------------------------------------------
# setting callbacks for different events to see if it works, print the message etc.
def on_connect_server (client, userdata, flags, rc, properties=None):
    print("Servidor::>>> CONNACK received with code %s." % rc)
    print ("Servidor::>>> Connect %s result is: %s" % (host, rc))
    if rc == 0:
        client.connected_flag = True
        print ("Servidor::>>> Connected OK")
        return
    
    print ("Servidor::>>> Failed to connect to %s, error was, rc=%s" % rc)
    
# with this callback you can see if your publish was successful
def on_publish_server (client, userdata, mid, properties = None):
    print("Servidor ::>>> mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe_server  (client, userdata, mid, granted_qos, properties = None):
    print("Servidor :::>> Subscribed: " + str(mid) + " " + str(granted_qos))
 
 
 # print message, useful cfor checking if it was successful
def main_server (server,topic,msg_in):
    """
        recv_evet_msg_json (msg_buzzer("a,b,c,d,e,f,g,A","1, 1, 1, 1, 1, 1, 2, 1","10"))
        recv_evet_msg_json (msg_servo (90))
        recv_evet_msg_json (msg_led_stick (0xFF00FF))
        recv_evet_msg_json (send_msg_json ('RTC',(EVENT_DTTEMP,23 )))
        recv_evet_msg_json (send_msg_json ('RTC',EVENT_DTLIGTH,23.2))
    """
    print("\n Servidor::>>> main - server:",server)
    print("Servidor::>>> main - topic:",topic)
    print("Servidor::>>> main - msg_in:",msg_in)
    inicio = time.time() #Medimos el tiempo que tarda en procesar un evento --123--
    event = recv_evet_msg_json (msg_in)
    if event  == EVENT_DANGPOS:
        logging.info ('DANGPOS')    
        logging.critical ('DANGPOS')  
        msg_out = send_drive_vision (server_id)
    elif event  == "DROWSINESS":
        logging.info ('DROWSINESS')    
        logging.critical ('DROWSINESS')  
        msg_out = send_drowiness (server_id)
    elif event  == 'DTBLINK':
        logging.info ('DTBLINK')
        logging.critical ('DTBLINK')  
        msg_out = send_dtblink (server_id)
    elif event  == 'DTYAWN':
        logging.info ('DTYAWN')
        logging.critical ('DTYAWN') 
        msg_out = send_dtyawn (server_id)
    elif event  == 'DTSMOKING':
        logging.info ('DTSMOKING')
        logging.critical ('DTSMOKING') 
        msg_out = send_dtsmoking ()
    elif event  == 'DTDRINK':
        logging.info('DTDRINK')
        logging.critical ('DTDRINK')
        msg_out = send_dtdrink ()
    elif event  == 'DTEATING':
        logging.info('DTEATING')
        logging.critical ('DTEATING')
        msg_out = send_dteating ()
    elif event  == 'DTMOBIL':
        logging.info('DTMOBIL')
        logging.critical ('DTMOBIL')
        msg_out = send_dtmobil ()
    elif event  == 'DTLIGTH':
        logging.info('DTLIGTH')
        logging.critical ('DTLIGTH')
        msg_out = send_dtligth (msg_in)
    elif event  == 'DTTEMP':
        logging.info('DTTEMP')
        logging.critical ('DTTEMP')
        msg_out = send_dttemp (msg_in)
    else:
        logging.info('error')
      
    if len (msg_out) != 0:
     send_cloudmseg (topic_pub_server,msg_out)
    fin = time.time()
    
    ss_time = f'Thread:{threading.get_ident()}-EVENT:{event}-TIME:{fin-inicio}'
    print(ss_time) # -123-- tiempo en procesar un vevento cualquiera
    logging.critical (ss_time)
    
def on_message_server (client, userdata, msg):
    str_msg = str(msg.payload.decode("utf-8"))
    print(f' Thread {threading.get_ident()} - Processing on_message')
     
    print(str_msg)
    if  str_msg  is None:
        print("Servidor::>>> NOT str_msg")    
    else:
        print("Servidor::>>> str_msg")
        
        print("Servidor:::>>>>> Message received %s from topic %s" % (msg.topic, str_msg) )
        pub_server = threading.Thread(target = main_server,args=(server,topic_pub_server,str_msg))
        pub_server.start ()   
        #main_server (server,topic_pub_server,str_msg)
        
def subscribing_server   (client,topic):
    client.on_message   = on_message_server
    client.on_subscribe = on_subscribe_server  
    client.subscribe(topic, qos=0)
    #OJO!!! En esta parte sirve añadir esta instrucción ya que son todo eventos. Pero en pynq es otra arquitectura
    client.loop_forever() 
    
def connect_hivemqtt ():
 global server
 global send_msgg_scr
 
 send_msgg_scr = threading.Semaphore()  # Para publicar mesajes mediante diferentes hilos en exclusión y con sección critica (la publicación)
 
 # using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
 # userdata is user defined data of any type, updated by user_data_set()
 # client_id is the given name of the client
 server = paho.Client (client_id=server_id, userdata=None, protocol=paho.MQTTv5)
 server.on_connect = on_connect_server 
 # enable TLS for secure connection
 server.tls_set (tls_version=mqtt.client.ssl.PROTOCOL_TLS)
 # set username and password
 server.username_pw_set (user_name, password)
 # connect to HiveMQ Cloud on port 8883 (default for MQTT)
 server.connect (host, port, keepalive = 60)
 server.connected_flag = False
 while not server.connected_flag: #wait in loop
     server.loop()#server.loop_start()
     sleep (1)
  
  
def send_cloudmseg (topic,msg_out):
    send_msgg_scr.acquire()
    logging.info("send_cloudmseg")
    logging.info(msg_out)
    if msg_out is not None and len (msg_out) > 0:
        for i in range(0,len(msg_out)):
            msg = msg_out [i]
            logging.info(msg)
            time.sleep(1)
            server.publish (topic, payload = msg, qos=0)
    send_msgg_scr.release()
    
# Messages to PYNQ
#--------------------
def send_drive_vision (client_id):
    msg_out = []
    msg_out.append(msg_led_stick (color=int('0xFFFFFF',base=16),clientid=client_id)) # ALERTA PoSIBLE PROBLEMA CON EL CONDUCTOR
    msg_out.append(msg_buzzer("A,B,C,d,e,f,g,A,B,C,D,E,F,G","2,2,2,1,1,1,1,2,2,2,2,2,2,2","12","6",clientid = client_id))  
    msg_out.append(msg_servo (120))           # Posible Somnolencia, simulamos que movemos el coche
    return msg_out
   
def send_drowiness (client_id):
    msg_out = []
    msg_out.append(msg_led_stick (color=int('0xFFAA00',base=16),clientid=client_id)) # ALERTA MICROSUEÑO Posible Somnolencia
    msg_out.append(msg_buzzer("A,B,C,d,e,f,g,A,B,C","2,2,2,1,1,1,1,2,2,2","12","5",clientid = client_id))  
    msg_out.append(msg_servo (90))           # Posible Somnolencia, simulamos que movemos el coche
    return msg_out

def send_dtblink (client_id):
    msg_out = []
    msg_out.append(msg_led_stick (color=int('0xFF00FF',base=16),clientid=client_id)) # ALERTA PARPADEO  
    msg_out.append(msg_buzzer("A,B,C,d,e,f,g,A,B,C","2,2,2,1,1,1,1,2,2,2","12","1",clientid = client_id))   #Pitamos para que despierte
    return msg_out 

def send_dtyawn (client_id):
    msg_out = []
    msg_out.append(msg_led_stick (color=int('0x00FF00',base=16),clientid=client_id)) # ALERTA PARPADEO  
    msg_out.append(msg_buzzer("A,B,C,d,e,f,g,A,B,C","2,2,2,1,1,1,1,2,2,2","12","1",clientid = client_id))   #Pitamos para que despierte
    return msg_out

def send_dtsmoking ():
    msg_out = []    
    msg_out.append(msg_led_stick (int('FFFF00',base=16))) # ALERTA fumando -- COLOR AMARILLO #FFFF00
    msg_out.append(msg_buzzer("A,b,c,d,e,f,g,A","1,1,1,1,1,1,2,1","10","3"))   #Pitamos para avisar
    return msg_out

def send_dtdrink ():
    msg_out = []
    msg_out.append(msg_led_stick (int('0x00FFFF',base=16))) # ALERTA bebiendo -- COLOR AZUL CLARO #00FFFF
    msg_out.append(msg_buzzer("a,b,c,d,e,f,g,A","1,1,1,1,1,1,2,1","10","3"))   #Pitamos para avisar
    return msg_out

def send_dteating ():
    msg_out = []
    msg_out.append(msg_led_stick (int('0x008000',base=16) )) # ALERTA comiendo -- COLOR VERDE #008000
    msg_out.append(msg_buzzer("a,b,c,d,e,f,g,A","1,1,1,1,1,1,2,1","10","1"))   #Pitamos para avisar 
    return msg_out

def send_dtmobil ():
    msg_out = []
    msg_out.append(msg_led_stick (int('0xFF0000',base=16))) # ALERTA habalndo con movil -- COLOR ROJO #FF0000
    msg_out.append(msg_buzzer("a,b,c,d,e,f,g,A","1,1,1,1,1,1,2,1","10","3"))   #Pitamos para   avisar 
    return msg_out
 
def send_dtligth (msg_in):
    msg_out = []
    msg_out.append(msg_led_stick (int('0x000080',base=16))) # ALERTA luz interna -- COLOR AZUL OSCURO #000080
    inten = recv_intensity_msg_json (msg_in)
    msg_out.append(send_msg_json ('RTC',EVENT_DTLIGTH,inten))   # devolvemos la intensidad de luz marcada  
    return msg_out
 
def send_dttemp (msg_in):
    msg_out = []
    msg_out.append(msg_led_stick (int('0xFF00FF',base=16))) # ALERTA Temeratura interna -- COLOR ROSA #FF00FF
    temp = recv_temp_msg_json (msg_in)
    msg_out.append(send_msg_json ('RTC',EVENT_DTTEMP,temp))   # devolvemos la intensidad de luz marcada  
    return msg_out


#---------------------------------------------------------
# Build messages
#--------------------------------------------------
def msg_login (status,clientid='Client_01'):
    msg = json.loads(MSG_LOGIN)
    msg ['clientid'] = clientid
    msg ['event']    = EVENT_LOGIN
    msg ['status']   = status
 
    
    return json.dumps(msg)
  
def msg_buzzer (note,beats,tempo,count,clientid='Client_01'):
    msg = json.loads(MDG_RTC_JSON_BUZZER)
    msg ['clientid'] = clientid
    msg ['event'] = EVENT_BUZZER
    msg['paramms'][0] = note
    msg['paramms'][1] = beats
    msg['paramms'][2] = tempo
    msg['paramms'][3] = count
    return json.dumps(msg)

def msg_servo (angle,clientid='Client_01'):  
    msg = json.loads(MDG_RTC_JSON_SERVO)
    msg ['clientid'] = clientid
    msg ['event'] = EVENT_SERVO
    msg['paramms'][0] = angle
    
    return json.dumps(msg)

def msg_led_stick (color,clientid='Client_01'):   
    msg = json.loads(MDG_RTC_JSON_LED_STICK)
    msg ['clientid'] = clientid
    msg ['event'] = EVENT_LED_STICK
    msg['paramms'][0] = color
    
    return json.dumps(msg)
 
def send_msg_json (action='DTC',event=None,vparam=None,clientid='Client_01'):
    msg = None
    if vparam == None:
        msg = json.loads(MSG_DTC_JSON)
        msg ['event'] = event
    else:
        if event == EVENT_DTTEMP:
            msg = json.loads(MSG_DTC_TEMP)
            msg ['event'] = event  
            msg ['Temp']  = vparam
        elif event == EVENT_DTLIGTH:
            msg = json.loads(MSG_RTC_LIGHT_INT)
            msg ['event']  = event  
            msg ['ILight'] = vparam
        else:
            msg = json.loads(MSG_DTC_JSON)
            msg ['event'] = event
            
    if msg is not None:
        msg ['action'] = action 
        msg ['clientid'] = clientid
        
    json_temp = json.dumps(msg)
    
    return json_temp
 

def recv_evet_msg_json (msg):
    logging.info('recv_evet_msg_json')
    print ('\t\t --->',msg)
    str_msg = msg #str(msg.payload.decode("utf-8"))
    
    event = None
    if str_msg is not None:
        print("str_msg")
        msg_in  = json.loads(str_msg) #decode json data
        
        event = msg_in["event"]
         
        print('event',event)
    else:
        print("NOT str_msg")

    return event

def recv_login_msg_json (msg):
    logging.info('recv_login_msg_json')
    print ('\t\t --->',msg)
    str_msg = msg #str(msg.payload.decode("utf-8"))
    
    event = None
    if str_msg is not None:
        print("str_msg")
        msg_in  = json.loads(str_msg) #decode json data
        
        status = msg_in["status"]
         
        print('status',status)
    else:
        print("NOT str_msg")

    return status
   
def recv_intensity_msg_json (msg):
    logging.info('recv_intensity_msg_json')
     
    str_msg = msg #str(msg.payload.decode("utf-8"))
    logging.info (str_msg)
    paramms = None
    if str_msg is not None:
        print("str_msg")
        msg_in  = json.loads(str_msg) #decode json data
 
        ILight = msg_in["ILight"]
         
        print('ILight',ILight)
    else:
        print("NOT str_msg")

    return ILight

def recv_temp_msg_json (msg):
    logging.info('recv_temp_msg_json')
    print ('\t\t --->',msg)
    str_msg = msg #str(msg.payload.decode("utf-8"))
    
    paramms = None
    if str_msg is not None:
        print("str_msg")
        msg_in  = json.loads(str_msg) #decode json data
        logging.info(msg_in)
        print(msg_in)
        Temp = msg_in["Temp"]
         
        print('Temp',Temp)
    else:
        print("NOT str_msg")

    return Temp

def recv_params_msg_json (msg):
    logging.info('recv_params_msg_json')
    print ('\t\t --->',msg)
    str_msg = msg #str(msg.payload.decode("utf-8"))
    
    paramms = None
    if str_msg is not None:
        print("str_msg")
        msg_in  = json.loads(str_msg) #decode json data
 
        paramms = msg_in["paramms"]
         
        print('paramms',paramms)
    else:
        print("NOT str_msg")

    return paramms 

# Init MQTT (Comunicación eventos con PYNQ). Ceconecta topic :
# topic_sub_server      = "ADASJG01/Server/"  -> subscribe (obtiene mensajes de la pynq en referenca a los eventos de sensores controlados)
# topic_pub_server      = "ADASJG01/Pynq/"    -> publicar (enviar mensajes a la pynq en referenca a las acciones a tomar con los actuadores referenciados)
#---------------------------------------------------------
def off_subs_app_mqttonly ():
  # Envio mensaje de logout
  print("Enevio mensaje LOGOUT NOK")

  msg_out = []
  msg_out.append(msg_login (status="NOK")) # ALERTA PoSIBLE PROBLEMA CON EL
  #pub_server = threading.Thread(target = main_server,args=(server,topic_pub_server,str_msg))
  #pub_server.start ()  
  #server.publish (topic_pub_server, payload = msg, qos=0)
  send_cloudmseg (topic_pub_server,msg_out) #Se realiza sincrona porque simula el proeso de login, para arrancar realmente la app.
  print("Mensaje LOGOUT NOK enviado")

def init_subs_app_mqttonly ():
 connect_hivemqtt ()
 CONNECT_HIVEMQTT = True
 #Envio mensaje de Login OK
 
 print("Enevio mensaje LOGIN OK")
 
 msg_out = []
 msg_out.append(msg_login (status="OK")) # ALERTA PoSIBLE PROBLEMA CON EL
 #pub_server = threading.Thread(target = main_server,args=(server,topic_pub_server,str_msg))
 #pub_server.start ()  
 #server.publish (topic_pub_server, payload = msg, qos=0)
 send_cloudmseg (topic_pub_server,msg_out) #Se realiza sincrona porque simula el proeso de login, para arrancar realmente la app.
 print("Mensaje LOGIN OK enviado")
 
 print("CONNECT_HIVEMQTT:",CONNECT_HIVEMQTT)
 subscribing_server (server,topic_sub_server)
 #sub_server = threading.Thread(target = subscribing_server,args=(server,topic_sub_server))
 #sub_server.start ()
 
def init_subs_app ():
 connect_hivemqtt ()
 CONNECT_HIVEMQTT = True

 print("CONNECT_HIVEMQTT:",CONNECT_HIVEMQTT)
 subscribing_server (server,topic_sub_server)
 #sub_server = threading.Thread(target = subscribing_server,args=(server,topic_sub_server))
 #sub_server.start ()

def disconnect_mqtt():
 logging.info("disconnect_mqtt")
 server.connected_flag = False
 server.disconnect  ()
 server.unsubscribe(topic_sub_server)
 server.loop_stop ()
 

def isConnect ():
 print("isConnect ()")

 if 'server' in globals() or 'server' in locals():
  return server.connected_flag
 else:
  return False

 # Conexión comunicación UART-PYNQ |Problemas en 3.01
 #-----------------------------------------------------------------
uart_scr = threading.Semaphore() 

def disconnect_uart ():
 print ("def disconnect_uart ():")
 if 'uart' in globals() and (uart.isOpen () == True):
    print('El Puerto serie estaba abierto, voy a cerarlo primero')
    uart.close()

def connect_uart ():
 print ("def connect_uart ():")
 global uart
 uart_connect = False
 try: 
    disconnect_uart ()

    uart  = serial.Serial(PORT_UART , BAUD_SERIAL,timeout = 1)
    #uart = serial.Serial (port = port, baudrate = baud,bytesize = 8, timeout = 2, stopbits = serial.STOPBITS_ONE )

    sleep(Delay0) # Entre 1.5s a 2s

    print(PORT_UART,' is open',  uart.isOpen())
    print('Device conectado: %s ' % (uart.name))
    print('Dump de configuración:\n %s ' % (uart))
    print('\n###############################################\n')
    uart_connect = True
    print("uart_connect:",uart_connect)
 except TimeoutError as err:
    print ("Error Serial Connecct")
    print(f"Unexpected {err=}, {type(err)=}")
 
 except serial.SerialException as err:
    print('Port is not available')
    print(f"Unexpected {err=}, {type(err)=}")
 
 except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")
 finally:
    if 'uart' in globals() and uart.isOpen():
        print("done serial Connect")
        return uart_connect
    else:
       print("Not Connect")
       return uart_connect
 
def send_uart (ledRGB = 4, color = 4):
  """
      RGBLEDS_XGPIO_OFFSET = 0
      RGBLEDS_START_INDEX  = 4
      RGB_CLEAR    = 0
      RGB_BLUE     = 1
      RGB_GREEN    = 2
      RGB_CYAN     = 3
      RGB_RED      = 4
      RGB_MAGENTA  = 5
      RGB_YELLOW   = 6
      RGB_WHITE    = 7
      MAX_LEDS_RGB = 2

      rgbled_position = [4,5]
      
      
      Color ROJO  (4)  --> desconexión app
      Color GREEN (2)  --> conectamos MQTT y arrancamos la app
  """
  uart_scr.acquire()
  print("def send_uart (ledRGB = 4, color = 4)")
  str_tx = "[%d,%s]\n" % (ledRGB, color)
  print("str_tx:",str_tx)
  app_r = False
  uart.write(str_tx.encode('utf-8'))  # Encender el led RGB 'ledRGB' con el color 'color'

  if int(color) == RGB_BLUE:
   app_r= True

  sleep(Delay1) # Entre 1.5s a 2s
  input_data = uart.readline()
  sleep(Delay0) # Entre 1.5s a 2s

  print ('\nRetorno da serial:', input_data.decode())
  uart_scr.release ()
  return True 
 
 # Deteccion bostezos y somnolencia
 #--------------------------------------------------
def eye_aspect_ratio(eye):
    # Coordenadas verticales de la marca del ojo (X, Y)
    A = dist.euclidean(eye[1], eye[5])# Calcular la distancia euclidiana entre dos conjuntos
    B = dist.euclidean(eye[2], eye[4])
    # Calcular la distancia euclidiana entre niveles
    # Coordenadas horizontales de la marca del ojo (X, Y)
    C = dist.euclidean(eye[0], eye[3])
    # Cálculo de la relación de aspecto del ojo
    ear = (A + B) / (2.0 * C)
    # Devuelve la relación de aspecto de los ojos
    return ear
 
def mouth_aspect_ratio_(mouth):
    """
     Con esta formula cuando hablas lo detecta como bostezo. Mejor identificar más puntos de la boca
    """
    A = np.linalg.norm(mouth[2] - mouth[9])  # 51, 59
    B = np.linalg.norm(mouth[4] - mouth[7])  # 53, 57
    C = np.linalg.norm(mouth[0] - mouth[6])  # 49, 55
    mar = (A + B) / (2.0 * C)
    return mar

def mouth_aspect_ratio(mouth):
    # Compute the euclidean distances between the three sets
    # of vertical mouth landmarks (x, y)-coordinates
    A = np.linalg.norm(mouth[13] - mouth[19])
    B = np.linalg.norm(mouth[14] - mouth[18])
    C = np.linalg.norm(mouth[15] - mouth[17])

    # Compute the euclidean distance between the horizontal
    # mouth landmarks (x, y)-coordinates
    D = np.linalg.norm(mouth[12] - mouth[16])

    # Compute the mouth aspect ratio
    mar = (A + B + C) / (2 * D)

    # Return the mouth aspect ratio
    return mar

def run_drowsiness (event):
    """
       EVENT_DANGPOS    = "DANGPOS"  
       EVENT_DROWSINESS = 'DROWSINESS'
       EVENT_DTBLINK    = "DTBLINK"
       EVENT_DTYAWN     = "DTYAWN"
    """
    # Definir dos constantes
    # Relación de aspecto del ojo y Umbral de parpadeo
    # Nota, el umbral de parpadeo se debe de configurar por persona. A la hora de registrarse debe medirse dicho umbral
    # cada persona tiene un umbral diferente. Además, la luz ambiente afecta a la medición, con lo que mejor todo en grises
    # Edtaria bien probar una mascara antes de realiar los calculos para evitar tener mediciones toxicas por ruido (FUTURO)
    EYE_AR_THRESH        = 0.18#0.2
    EYE_AR_CONSEC_FRAMES = 4 #3
    # Relación de aspecto de bostezo y Umbral de bostezo
    MAR_THRESH = 0.5 #0.5 
    MOUTH_AR_CONSEC_FRAMES = 4#3
    # Inicialice el contador de frames y el número total de parpadeos
    COUNTER = 0
    TOTAL = 0
    # Inicializar contador de frames y bostezo total
    mCOUNTER = 0
    mTOTAL = 0
    
    #Conador de conductor sin visión o nodetectado y umbral asociado. 
    countDrive = 0
    DRIVE_CONSEC_FRAMES = 40
    inc_count  = 0
    # Nos creamos un publicador de eventos de la cam
    print("Voy a conectar el cliente publicador de eventos de la cam")
    connect_client_cam ()
    
    # Inicializamos el detector de rostro (HOG) de DLIB, luego cree la predicción de hitos faciales. utilizaremos la libreria 
    print("[INFO] loading facial landmark predictor...")
    # Paso 1: Usaremos dlib.get_frontal_face_detector () para obtener el detector de posición de la cara
    detector = dlib.get_frontal_face_detector()
    # Paso 2: Usaremos dlib.shape_predictor para obtener el detector de posición de la función facial
    predictor = dlib.shape_predictor('./model/shape_predictor_68_face_landmarks.dat') #Datos red darcknet preentrenada

    # Paso 3: Obtenemos los valores estandares de índices de los signos faciales del ojo izquierdo y derecho por separado
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

    # PAso 4: capturamos y obtenemos la cámara local cv2
    cap = cv2.VideoCapture(0)

    # Leemos frames a fremes el video en real time
    while True:
        if event.is_set():
            break
        # Paso 5: bucle, leer la imagen, ampliar la dimensión de la imagen y escala de grises
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=720)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Paso 6: Usamos  el detector (gris, 0) para la detección de la posición de la cara
        rects = detector(gray, 0)
        if len(rects) == 0:
            cv2.putText(frame, " Conductor NO DETECTADO!! RIESGO DE ACCIDENTE!!!", (20, 70),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (84, 255, 255), 2)
            cv2.imshow("Frame", frame)
            countDrive += 1
        else:
            countDrive = 0
         
        if countDrive > DRIVE_CONSEC_FRAMES: # DRIVE_CONSEC_FRAMES = 40 --- OJO!! hemos modificado los umbrales para desarrollo 
            cv2.putText(frame, " RIESGO DE ACCIDENTE!!!", (20, 170),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (146, 43, 33), 2)
            cv2.imshow("Frame", frame)
            if inc_count  < 2:
                inc_count +=1
            else:
                countDrive = 2
                inc_count  = 0
            #Enviamos mensaje alerta conductor sin visión o no detectado
            #print("Voy a enviar mensaje")
            m = send_drive_vision (client_cam_id)
            send_msg =  threading.Thread(target = send_cloud_cam_mseg,args=(m,))
            send_msg.start ()# Enviamos alerta de somnolencia  
            #send_cloud_cam_mseg (m)
            #print("Voy a enviar mensaje")
            mmsg = f'event:SLEEP, total:{TOTAL},mtotal:{mTOTAL}'
            
            logging.critical (EVENT_DANGPOS)
            logging.critical (mmsg)
            
        # Realmente el Rects tenemos más de una cara. En paso futuro hay que extraer aquella que corresponde al conductor (Si la hubiese) y compararla
        # con la almacenada en el sistema (Cuando se realizo el resgitro de rasgos faciales).
        # Paso 7: repita la información de la posición facial y use el predictor (gris, rect) para obtener la información de posición de la función facial
        for rect in rects:
            shape = predictor(gray, rect)

            shape = face_utils.shape_to_np(shape)

            # Paso 9: Extraemos las coordenadas de los ojos izquierdo y derecho
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            
            # Paso 10: Extraemos las coordenadas de boca
            mouth = shape[mStart:mEnd]


            # Paso 11: el constructor calcula el valor EAR de los ojos izquierdo y derecho. Utiliamos  el valor promedio como EAR final
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
            # Paso 12:REalizamos el mismo paso para el caso de la boca
            mar = mouth_aspect_ratio(mouth)

            # Paso 13: Usamos cv2.convexHull para obtener la posición del casco convexo, y con drawContours dibujamos la posición del contorno 
            leftEyeHull  = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            
            # Paso 14: Idem con la boca
            mouthHull = cv2.convexHull(mouth)
            cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)

            # Paso 15:  Recuadramos la cara que estamos evaluando (EN futuro, debemos de compararla con al del conductor registrado)
            left = rect.left()
            top = rect.top()
            right = rect.right()
            bottom = rect.bottom()
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)    

            '''
                A partir de aqui realizamos los cálculos de fatiga.
            '''
            # PAso 16: Si el valor de ear calculado es menor al umbral establecido para dicho conductor entonces incrementamos nñumero de parpadeos
            if ear < EYE_AR_THRESH:# Relación de aspecto del ojo: el normal 0.2, para ojos pequeños 0.1
                COUNTER += 1
            else:
                # Si es inferior al umbral por EYE_AR_CONSEC_FRAMES veces consecutivas, significa que se ha realizado una actividad de parpadeo
                if COUNTER >= EYE_AR_CONSEC_FRAMES:# Umbral: 3, OJO!! hemos modificado los umbrales para desarrollo
                    TOTAL += 1 # Nos indica las veces que ha parpadeado cada EYE_AR_CONSEC_FRAMES consecutivos
                    #print("--------------------Voy a enviar mensaje")
                    m = send_dtblink (client_cam_id)
                    send_msg =  threading.Thread(target = send_cloud_cam_mseg,args=(m,))
                    send_msg.start ()# Enviamos alerta de parpadeo  
                    #send_cloud_cam_mseg (m)
                    #print("--------------------Voy a enviar mensaje")
                    mmsg = f'event:BLINK,total:{TOTAL},mtotal:{mTOTAL}'
                    
                    logging.critical (EVENT_DTBLINK)
                    logging.critical (mmsg)
                # Restablecer contador de marco de ojo
                COUNTER = 0

            # Paso 14: Sacamos por pantalla utilizando cv2.putText el número de parpadeos y el valor del ear obtenido en el frame
            cv2.putText(frame, "Faces: {}".format(len(rects)), (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "Blinks: {}".format(TOTAL), (150, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "COUNTER: {}".format(COUNTER), (300, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2) 
            cv2.putText(frame, "EAR: {:.2f}".format(ear), (455, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            mmsg = f'event:INFO,Blinks:{TOTAL},COUNTER:{COUNTER},EAR:{ear}'
            logging.critical (mmsg)
            
            '''
Calculamos la puntuación de boca abierta, si es menor que el umbral, se incrementa en 1; si es menor que el umbral por MOUTH_AR_CONSEC_FRAMES veces consecutivas, significa que se produce un bostezo, y el mismo bostezo es de aproximadamente MOUTH_AR_CONSEC_FRAMES frames.
            '''
            # Paso 15: Del mismo modo comprobamos si se ha producio un bostezo    
            if mar > MAR_THRESH:# Umbral de boca abierta 0.5
                mCOUNTER += 1
                cv2.putText(frame, "Yawning!", (10, 60),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                mmsg = f'event:Yawning,total:{TOTAL},mtotal:{mTOTAL}'
                logging.critical (mmsg)
            else:
                # Si es inferior al umbral por 3 veceprint("--------------------Voy a enviar mensaje")s consecutivas, significa un bostezo
                if mCOUNTER >= MOUTH_AR_CONSEC_FRAMES:# Umbral: 3 --- OJO!! hemos modificado los umbrales para desarrollo
                    mTOTAL += 1
                    mmsg = f'event:YAWN,total:{TOTAL},mtotal:{mTOTAL}'
                    logging.critical (EVENT_DTYAWN)
                    logging.critical (mmsg)
                    #print("--------------------Voy a enviar mensaje")
                    m = send_dtyawn (client_cam_id)
                    send_msg =  threading.Thread(target = send_cloud_cam_mseg,args=(m,))
                    send_msg.start ()# Enviamos alerta de bostezo 
                    #send_cloud_cam_mseg (m)
                    #print("--------------------Voy a enviar mensaje")
                # Restablecer contador de marco de boca
                mCOUNTER = 0
            cv2.putText(frame, "Yawning: {}".format(mTOTAL), (150, 60),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "mCOUNTER: {}".format(mCOUNTER), (300, 60),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2) 
            cv2.putText(frame, "MAR: {:.2f}".format(mar), (480, 60),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            mmsg = f'event:INFO,Yawning:{mTOTAL},mCOUNTER:{mCOUNTER},mar:{mar}'
            logging.critical (mmsg)
            #  Paso 16: operación de dibujo, 68 identificación de puntos de características de dlib (Futuro poner mediapipe en la pynq)
            for (x, y) in shape:
                cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

           #print('Relación de aspecto en tiempo real de la boca: {: .2f}'.format(mar)+"\ topen tu boca:"+str([False,True][mar > MAR_THRESH]))
           # print('Relación de aspecto en tiempo real de los ojos: {: .2f}'.format(ear)+"\ tBlink:"+str([False,True][COUNTER>=1]))

        # Determinar consejos de fatiga
        # TOTAL >= 20 or mTOTAL>=10:
        if TOTAL >= 35 or mTOTAL>=15:
            cv2.putText(frame, "SLEEP!!!. Riesgo Acidente!!!", (100, 200),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            #Enviamos mensaje alerta microsueño y lo guardamos en el log
            #print("Voy a enviar mensaje")
            m = send_drowiness (client_cam_id)
            send_msg =  threading.Thread(target = send_cloud_cam_mseg,args=(m,))
            send_msg.start ()# Enviamos alerta de somnolencia  
            #send_cloud_cam_mseg (m)
            #print("Voy a enviar mensaje")
            mmsg = f'event:SLEEP, total:{TOTAL},mtotal:{mTOTAL}'
            
            logging.critical (EVENT_DROWSINESS)
            logging.critical (mmsg)
           
        # Presione q para salir
        #cv2.putText(frame, "Press 'q': Quit", (20, 500),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (84, 255, 159), 2)
        # Muestra de ventana con opencv
        cv2.imshow("Frame", frame)

        # if the `q` key was pressed, break from the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release camera release camera
    cap.release()
    # do a bit of cleanup
    cv2.destroyAllWindows()


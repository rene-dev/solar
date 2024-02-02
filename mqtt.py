#!/bin/env python3
import paho.mqtt.client as mqtt
from time import sleep
import json
import socket

battery = {}
power = 0.0

#rechts
HOST = "192.168.177.89"  # The server's hostname or IP address
PORT = 8000  # The port used by the server

def crc16(data):
  crc=0x0
  for c in data:
    crc=crc^(c<<8)
    for j in range(8): crc=(crc<<1)^0x1021 if crc & 0x8000 else crc<<1
  crc = crc & 0xFFFF
  return crc

def on_connect(client, userdata, flags, rc):
    client.subscribe([("pylontech/#",0),("trifasipower",0)])

def on_message(client, userdata, msg):
    global power
    global battery
    if msg.topic == "trifasipower":
        power = json.loads(msg.payload)['Q']['total']
        print(power)
    elif 'pylontech' in msg.topic:
        #print(f'{msg.topic=} {msg.payload=}')
        battery[msg.topic.split('/')[2]] = float(msg.payload)
        #print(battery)
        #print(msg.topic.split('/')[2]+" "+str(msg.payload))

client = mqtt.Client("solarfoo")
client.connect('192.168.177.2')
client.username_pw_set('pwr', 'pwr')
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    sleep(5)
    while True:
      max_feed = 10000
      cmd_feed = int(power)
      #print(cmd_feed)
      eminfo = f"^S026EMINFO00000,{max_feed:05},{1 if cmd_feed > 0 else 0},{abs(cmd_feed):05}\r"
      print(eminfo)
      s.sendall(eminfo.encode())
      print(s.recv(1024))
      sleep(0.5)
      print("BMS:")
      soc = int(battery['SOC'])
      volt = int(battery['voltage_module']*10)#422
      cd = 0 #charge/discharge
      current = 0
      maxdis = int(battery['Dischargelimit'])
      cutoff = 450#44-45
      stopch = 0#geht b
      stopdis = 0#geht b
      maxchg = int(battery['Chargelimit']*10)#geht
      floatv = 525#51 float 52 abs
      cv = int(battery['Chargevoltage']*10)
      force_charge = 0#geht b
      warning = 0
      if int(battery['Chargelimit']) <= 10 or soc >= 99:
        print('limiter')
        stopch = 1
        maxchg = 0
      if int(battery['Dischargelimit']) <= 10 or soc <= 20:
        print('limiter-')
        stopdis = 1
        maxdis = 0

      cmd = f"^D054BMS{volt:04},{soc:03},{cd},{current:04},{warning:01},{force_charge},{cv:04},{floatv:04},{maxchg:04},{stopdis},{stopch},{cutoff:04},{maxdis:04}".encode()
      print(f'{cmd=}')
      crc = crc16(cmd)
      cmd = cmd + (crc >> 8).to_bytes(1) + (crc&0xff).to_bytes(1) + b'\r'
      s.sendall(cmd)
      sleep(0.5)
      s.sendall(b"^P004BMS\r")
      data = s.recv(1024)
      print(f'{data=}')



#while True:
#    sleep(1)
    #print("a")


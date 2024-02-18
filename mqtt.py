#!/bin/env python3
import paho.mqtt.client as mqtt
from time import sleep
import json
import socket
from contextlib import ExitStack

battery = {}
power = 0.0
rse_limit = 100
rse_limit_send = 0
kwp_total = 29580

def crc16(data):
  crc=0x0
  for c in data:
    crc=crc^(c<<8)
    for j in range(8): crc=(crc<<1)^0x1021 if crc & 0x8000 else crc<<1
  crc = crc & 0xFFFF
  return crc

def on_connect(client, userdata, flags, rc):
    client.subscribe([("pylontech/#",0),("trifasipower",0),("rundfunk/scale",0)])

def on_message(client, userdata, msg):
    global power
    global battery
    global rse_limit
    if msg.topic == "trifasipower":
        power = json.loads(msg.payload)['Q']['total']
        #print(power)
    elif 'pylontech' in msg.topic:
        #print(f'{msg.topic=} {msg.payload=}')
        battery[msg.topic.split('/')[2]] = float(msg.payload)
        #print(battery)
        #print(msg.topic.split('/')[2]+" "+str(msg.payload))
    elif 'rundfunk' in msg.topic:
        #print(f'{msg.topic=} {msg.payload=}')
        rse_limit = float(msg.payload)
        #print(f'{rse_limit=}')
        #print(msg.topic.split('/')[2]+" "+str(msg.payload))

client = mqtt.Client("solarfoo")
client.connect('192.168.177.2')
client.username_pw_set('pwr', 'pwr')
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as l, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as r:
    l.connect(('solar232links', 8000))
    r.connect(('solar232rechts', 8000))
    s = r
    sleep(5)

    sleep(1)
    while True:
      if rse_limit != rse_limit_send:
        limit = min(10000,kwp_total/2.0 * rse_limit/100.0)
        print(f'setting feed limit to {limit}')
        rse_limit_send = rse_limit
        #print("maxfeed")
        cmd_maxfeed = f'^S011GPMP{int(limit):06}\r'  #  b'^1\x0b\xc2\r'
        s.sendall(cmd_maxfeed.encode())
        print(s.recv(1024))
        l.sendall(cmd_maxfeed.encode())
        print(l.recv(1024))
        #print("maxfeed")

      max_feed = 10000
      cmd_feed = int(power)
      #print(cmd_feed)
      eminfo = f"^S026EMINFO00000,{max_feed:05},{1 if cmd_feed > 0 else 0},{abs(cmd_feed):05}\r"
      #print(eminfo)
      s.sendall(eminfo.encode())
      reply = s.recv(1024)
      #print(reply)
      sleep(0.5)
      #print("BMS:")
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
      if int(battery['Chargelimit']) <= 10 or soc >= 100:
        print('battery full')
        stopch = 1
        maxchg = 0
      if int(battery['Dischargelimit']) <= 10 or soc <= 20:
        print('battery low')
        stopdis = 1
        maxdis = 0

      cmd = f"^D054BMS{volt:04},{soc:03},{cd},{current:04},{warning:01},{force_charge},{cv:04},{floatv:04},{maxchg:04},{stopdis},{stopch},{cutoff:04},{maxdis:04}".encode()
      #print(f'{cmd=}')
      crc = crc16(cmd)
      cmd = cmd + (crc >> 8).to_bytes(1) + (crc&0xff).to_bytes(1) + b'\r'
      s.sendall(cmd)
      sleep(0.5)
      s.sendall(b"^P004BMS\r")
      data = s.recv(1024)
      #print(f'{data=}')



#while True:
#    sleep(1)
    #print("a")


#!/bin/env python3
"""
  can0  359   [7]  00 00 00 00 04 50 4E
  can0  351   [8]  14 02 B0 04 40 06 C2 01
  can0  355   [4]  5A 00 64 00
  can0  356   [6]  84 13 F1 FF 37 00
  can0  35C   [2]  C0 00
  can0  35E   [8]  50 59 4C 4F 4E 20 20 20
"""
import can
import ctypes
import struct
import sys
import json
from paho.mqtt import client as mqtt_client

#sudo ip link set can0 up type can bitrate 500000 sample-point 0.875
bus = can.Bus(interface='socketcan',channel='can0',bitrate=500000)

broker = '192.168.177.2'
port = 1883
topic = "test"
# generate client ID with pub prefix randomly
client_id = 'python-mqtt-pylontech'
username = 'pwr'
password = 'pwr'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(rc)
            print(flags)
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topic, msg, retain=False):
    result = client.publish(topic, msg, retain=retain)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic} {result}")


client = connect_mqtt()

convert = {
   0x351 : {
        'Chargevoltage':{
            'convert': lambda d: struct.unpack('<H',d[0:2])[0]*0.1,
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "icon": "mdi:battery",
            "unique_id": "eikao4Qu",
            "value_template": "{{value|round(2)}}"
        },
        'Chargelimit':{
            'convert': lambda d: struct.unpack('<h',d[2:4])[0]*0.1,
            "device_class": "current",
            "unit_of_measurement": "A",
            "icon": "mdi:battery",
            "unique_id": "ailie7IH",
            "value_template": "{{value|round(2)}}"
        },
        'Dischargelimit':{
            'convert': lambda d: struct.unpack('<h',d[4:6])[0]*0.1,
            "device_class": "current",
            "unit_of_measurement": "A",
            "icon": "mdi:battery",
            "unique_id": "Ing7geis",
            "value_template": "{{value|round(2)}}"
        },
   },
   0x355 : {
        'SOC':{
            'convert': lambda d: struct.unpack('<H',d[0:2])[0],
            "device_class": "battery",
            "unit_of_measurement": "%",
            "icon": "mdi:battery",
            "unique_id": "Eizusai8",
            "value_template": "{{value|round(2)}}"
        },
        'SOH':{
            'convert': lambda d: struct.unpack('<H',d[2:4])[0],
            "device_class": "battery",
            "unit_of_measurement": "%",
            "icon": "mdi:battery",
            "unique_id": "OozaiK2S",
            "value_template": "{{value|round(2)}}"
        },
   },
   0x356 : {
        'voltage_module':{
            'convert': lambda d: struct.unpack('<h',d[0:2])[0]*0.01,
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "icon": "mdi:battery",
            "unique_id": "rai7eeJi",
            "value_template": "{{value|round(2)}}"
        },
        'current_module':{
            'convert': lambda d: struct.unpack('<h',d[2:4])[0]*0.1,
            "device_class": "current",
            "unit_of_measurement": "A",
            "icon": "mdi:battery",
            "unique_id": "lael8Ieb",
            "value_template": "{{value|round(2)}}"
        },
        'temperature_module':{
            'convert': lambda d: struct.unpack('<h',d[4:6])[0]*0.1,
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "icon": "mdi:thermometer",
            "unique_id": "ieY6oxoo",
            "value_template": "{{value|round(2)}}"
        },
   },
}

state_topic = {}
value_cache = {}

for key,values in convert.items():
    for name, value in values.items():
        state_topic[name] = {
            "name": name,
            "state_topic": f"pylontech/sensor/{name}/value",
            "device_class": value["device_class"],
            "unit_of_measurement": value["unit_of_measurement"],
            "icon": value["icon"],
            "unique_id": value["unique_id"],
            "device": {
                "identifiers": "ho3eiLai", 
                "name": "Batterie",
                "model": "US5000",
                "manufacturer": "Pylontech"}
            }
        if "value_template" in value:
            state_topic[name]["value_template"] = value["value_template"]
        publish(client, f"homeassistant/sensor/{name}/config", json.dumps(state_topic[name], ensure_ascii=False), retain=True)

print("start")
while True:
    message = bus.recv(timeout=0.1)
    #print("msg")
    if message:
        if message.arbitration_id in convert.keys():
            for name, measurement in convert[message.arbitration_id].items():
                value = measurement['convert'](message.data)
                value_cache[name] = value
                print(name, value)
                publish(client, state_topic[name]['state_topic'], value)
        else:
            pass
            #print("unknown message: {}".format(message))
    else:
        print(value_cache)

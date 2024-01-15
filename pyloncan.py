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


# def publish(client):
#     msg_count = 0
#     while True:
#         time.sleep(1)
#         msg = f"messages: {msg_count} BEMIS!!!!"
#         result = client.publish(topic, msg)
#         # result: [0, 1]
#         status = result[0]
#         if status == 0:
#             print(f"Send `{msg}` to topic `{topic}`")
#         else:
#             print(f"Failed to send message to topic {topic}")
#         msg_count += 1


def publish2(client, topic, msg, retain=False):
    result = client.publish(topic, msg, retain=retain)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic} {result}")


client = connect_mqtt()
#client.loop_start()

convert = {
   0x351 : {
        'Chargevoltage':{
            'convert': lambda d: struct.unpack('<H',d[0:2])[0]*0.1,
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "icon": "mdi:battery",
            "unique_id": "eikao4Qu",
        },
        'Chargelimit':{
            'convert': lambda d: struct.unpack('<h',d[2:4])[0]*0.1,
            "device_class": "current",
            "unit_of_measurement": "A",
            "icon": "mdi:battery",
            "unique_id": "ailie7IH",
        },
        'Dischargelimit':{
            'convert': lambda d: struct.unpack('<h',d[4:6])[0]*0.1,
            "device_class": "current",
            "unit_of_measurement": "A",
            "icon": "mdi:battery",
            "unique_id": "Ing7geis",
        },
   },
   0x355 : {
        'SOC':{
            'convert': lambda d: struct.unpack('<H',d[0:2])[0],
            "device_class": "battery",
            "unit_of_measurement": "%",
            "icon": "mdi:battery",
            "unique_id": "Eizusai8",
        },
        'SOH':{
            'convert': lambda d: struct.unpack('<H',d[2:4])[0],
            "device_class": "battery",
            "unit_of_measurement": "%",
            "icon": "mdi:battery",
            "unique_id": "OozaiK2S",
        },
   },
   0x356 : {
        'voltage_module':{
            'convert': lambda d: struct.unpack('<h',d[0:2])[0]*0.01,
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "icon": "mdi:battery",
            "unique_id": "rai7eeJi",
        },
        'current_module':{
            'convert': lambda d: struct.unpack('<h',d[2:4])[0]*0.1,
            "device_class": "current",
            "unit_of_measurement": "A",
            "icon": "mdi:battery",
            "unique_id": "lael8Ieb",
        },
        'temperature_module':{
            'convert': lambda d: struct.unpack('<h',d[4:6])[0]*0.1,
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "icon": "mdi:thermometer",
            "unique_id": "ieY6oxoo",
        },
   },
}

state_topic = {}

for key,values in convert.items():
    for name, value in values.items():
        state_topic[name] = {
            "name": name,
            "state_topic": f"pylontech/sensor/{name}/value",
            "device_class": value["device_class"],
            "unit_of_measurement": value["unit_of_measurement"],
            #"value_template": value["value_template"],
            "icon": value["icon"],
            "unique_id": value["unique_id"],
            "device": {
                "identifiers": "ho3eiLai", 
                "name": "Batterie",
                "model": "US5000",
                "manufacturer": "Pylontech"}
            }
        publish2(client, f"homeassistant/sensor/{name}/config", json.dumps(state_topic[name], ensure_ascii=False), retain=True)

#sys.exit()

# for key,value in convert.items():
#     state_topic[key] = {"name": value["name"],
#                         "state_topic": f"pylontech/sensor/{name}/value",
#                         "device_class": value["device_class"],
#                         "unit_of_measurement": value["unit_of_measurement"],
#                         #"value_template": value["value_template"],
#                         "icon": value["icon"],
#                         "unique_id": value["unique_id"],
#                         "device": {"identifiers": "ho3eiLai", 
# 								   "name": "Heizung",
#                                    "model": "PI",
#                                    "manufacturer": "Junkers feat Bemistec Unlimited Enterprises"}
#                         }
    ###publish2(client, f"homeassistant/sensor/{value['name']}/config", json.dumps(state_topic[key], ensure_ascii=False), retain=True)

#print (state_topic)

    # publish2(client, "homeassistant/sensor/heizung_temp3/config", '{"name": "Temp_3", "state_topic": "homeassistant/sensor/heizung/state", "device_class": "temperature", "unit_of_measurement": "°C", "value_template": "{{ value_json.temperature}}", "unique_id": "dztstzhdetsrthsss22", "device": {"identifiers": "834242st333hsv", "name": "devicename_temp_3", "sw_version": "0.00000000001", "model": "lars laptop", "manufacturer": "lars"}}', retain=True)
    # publish2(client, "homeassistant/sensor/heizung_temp4/config", '{"name": "Temp_4", "state_topic": "homeassistant/sensor/heizung/state", "device_class": "temperature", "unit_of_measurement": "°C", "value_template": "{{ value_json.temperature}}", "unique_id": "dztgrhsgfrthsss22", "device": {"identifiers": "834242st333hsv", "name": "Heizung", "model": "PI", "manufacturer": "Junkers feat Bemistec Unlimited Enterprises"}}', retain=True)


#for key,value in state_topic:
#    publish2(client, "homeassistant/sensor/heizung_temp1/config", json.dumps(config, ensure_ascii=False), retain=True)

#sys.exit(0)
print("start")
while True:
    message = bus.recv()
    #print("msg")
    if message.arbitration_id in convert.keys():
        for name, measurement in convert[message.arbitration_id].items():
            print(name, measurement['convert'](message.data))
            value = measurement['convert'](message.data)
        # key = convert[message.arbitration_id]['name']
        # value = convert[message.arbitration_id]['convert'](message.data)
        # #print ("{} {}".format(key,value))
        # json_body = [
        # {
        #     'measurement': "heizwerte",
        #     'tags': {
        #         'location': "vorne"
        #     },
        #     'fields': {
        #         key: value,
        #     }
        # }
        # ]
        #print(json_body)
            print(state_topic[name]['state_topic'])
            publish2(client, state_topic[name]['state_topic'], value)
    else:
        pass
        #print("unknown message: {}".format(message))
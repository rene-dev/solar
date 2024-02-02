#!/bin/bash
source /home/solar/mpp/venv/bin/activate
mpp-solar -P pi17infini -p /dev/rechts -c PS#GS#MOD#WS --porttype=hidraw -n rechts -T rechts -o hassd_mqtt -q homebemis --mqttuser pwr --mqttpass pwr
mpp-solar -P pi17infini -p /dev/links  -c PS#GS#MOD#WS --porttype=hidraw -n links  -T links  -o hassd_mqtt -q homebemis --mqttuser pwr --mqttpass pwr


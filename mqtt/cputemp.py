#!/usr/bin/python
import sys
import paho.mqtt.client as mqtt

# parameters
sensor_idx  = 5
cpuTemp = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000.0

mqtt_msg    = '{{"idx":{},"nvalue":1,"svalue":"{:.1f};0;0"}}'

client = mqtt.Client("cpu_temp.py")
client.connect("localhost")
msg = mqtt_msg.format(sensor_idx, cpuTemp)
client.publish("domoticz/in", msg)

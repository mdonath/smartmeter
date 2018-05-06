#!/usr/bin/python
import sys
import Adafruit_DHT
import paho.mqtt.client as mqtt

# parameters
sensor_idx  = 4
DHT_type    = 22
OneWire_pin = 22
mqtt_msg    = '{{"idx":{},"nvalue":1,"svalue":"{:.1f};{:.1f};0"}}'

# read dht22 temperature and humidity
humidity, temperature = Adafruit_DHT.read_retry(DHT_type, OneWire_pin)

if humidity is not None and temperature is not None:
	client = mqtt.Client("dht22.py")
	client.connect("localhost")
	msg = mqtt_msg.format(sensor_idx, temperature, humidity)
	client.publish("domoticz/in", msg)

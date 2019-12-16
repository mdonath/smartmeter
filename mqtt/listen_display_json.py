#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from Adafruit_LED_Backpack import SevenSegment, HT16K33
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage
import json
import re

#####################################
# DOCUMENTATION
#####################################
# {
#	"colon": false,
#	"left_colon": false,
#	"fixed_decimal": false,
#	"invert": false,
#	"brightness": 1,
#	"blinkRate": 0,
#	"justify_right": true
#	"number_str": "1234",
#	"float": 12.34,
#	"hex": "0xDEAD",
#	"digit_num": [ 1, "-", 3, "F" ],
#	"digit_raw": [ 118,121,56,115 ]
# }
#####################################

LED_TOPIC = "home/sevensegment/display"


def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
 	# print("Received message: " + msg)

	try:
		json_message = json.loads(msg)
	except ValueError as e:
		if re.match('\d\d:\d\d', msg):
			json_message = {
				"colon": True,
				"left_colon": False,
				"fixed_decimal": False,
				"blink_rate": 0,
				"digit_num": [ msg[:1], msg[1:2], msg[3:4], msg[4:5] ]
			}
		elif re.match('\d\d\.\d\d°C', msg): # 22.50°C
			json_message = {
				"colon": True,
				"left_colon": False,
				"fixed_decimal": True,
				"blink_rate": 0,
				"digit_num": [ msg[:1], msg[1:2], msg[3:4], "C"] }
		else: # error
			json_message = {
				"blink_rate": 2,
				"digit_raw": [ 121, 51, 51, 0]
			}

	colon = json_message.get('colon')
	if colon != None:
		display.set_colon(colon)
 
	left_colon = json_message.get('left_colon')
	if left_colon != None:
		display.set_left_colon(left_colon)

	fixed_decimal = json_message.get('fixed_decimal')
	if fixed_decimal != None:
		display.set_fixed_decimal(fixed_decimal)

	brightness = json_message.get('brightness')
	if brightness != None:
		value = int(brightness)
		if value >= 0 or value <= 15:
			display.set_brightness(value)
		
	invert = json_message.get('invert')
	if invert != None:
		display.set_invert(invert)
		
	blink_rate = json_message.get('blink_rate')
	if blink_rate != None:
		value = int(blink_rate)
		if value >= 0 or value <= 3:
			rate = [HT16K33.HT16K33_BLINK_OFF,
				HT16K33.HT16K33_BLINK_2HZ,
				HT16K33.HT16K33_BLINK_1HZ,
				HT16K33.HT16K33_BLINK_HALFHZ][value]
			display.set_blink(rate)

	justify_right = json_message.get('justify_right')
	if justify_right == None:
		justify_right = True	

	number_str = json_message.get('number_str')
	if number_str != None:
		display.print_number_str(number_str, justify_right)

	float_str = json_message.get('float')
	if float_str != None:
		decimal_digits = json_message.get('float_decimal_digits')
		if decimal_digits == None:
			decimal_digits = 2
		display.print_float(float_str, decimal_digits, justify_right)

	hex_str = json_message.get('hex')
	if hex_str != None:
		value = int(hex_str, 0)
		display.print_hex(value, justify_right)

	digit_num = json_message.get('digit_num')
	if digit_num != None:
		for i, v in enumerate(digit_num):
			display.set_digit(i, v)

	digit_raw = json_message.get('digit_raw')
	if digit_raw != None:
		for i, v in enumerate(digit_raw):
			display.set_digit_raw(i, v)

	# finally: write changes to the display
	try:
		display.write_display()
	except:
		print("Fout opgetreden")

def test_message():
	message = MQTTMessage()

	on_message(None, None, message)


if __name__ == '__main__':
	mqttc = mqtt.Client("7segment-display")
	mqttc.on_message = on_message
	mqttc.connect("mqtt")
	mqttc.subscribe(LED_TOPIC)

	display = SevenSegment.SevenSegment()
	display.begin()
	display.set_brightness(1)
	display.print_number_str("----")
	display.write_display()

	mqttc.loop_forever()


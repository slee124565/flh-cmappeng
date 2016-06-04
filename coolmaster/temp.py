#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  temp_LED.py
#
# Use a thermistor to read temperatures and illuminate
# a number of LEDs based upon the returned temperature
#
#  Copyright 2015  Ken Powers
#
 
import time, math

import RPi.GPIO as GPIO
 
# Set GPIO pins to Broadcom numbering system
GPIO.setmode(GPIO.BCM)
 
# Define our constants
RUNNING = True
led_list = [17,27,22,10,9,11,13,26] # GPIO pins for LEDs
temp_low = 70 # Lowest temperature for LEDs (F)
temp_high = 86 # Highest temperature for LEDs (F)
a_pin = 23
b_pin = 24
# Set up our LED GPIO pins as outputs
for x in range(0,8):
    GPIO.setup(led_list[x], GPIO.OUT)
    GPIO.output(led_list[x], GPIO.LOW)

 
# Try to keep this value near 1 but adjust it until
# the temperature readings match a known thermometer
adjustment_value = 0.97
 
# Create a function to take an analog reading of the
# time taken to charge a capacitor after first discharging it
# Perform the procedure 100 times and take an average
# in order to minimize errors and then convert this
# reading to a resistance
def resistance_reading():
    
    total = 0
    for i in range(1, 100):
        # Discharge the 330nf capacitor
        GPIO.setup(a_pin, GPIO.IN)
        GPIO.setup(b_pin, GPIO.OUT)
        GPIO.output(b_pin, False)
        time.sleep(0.01)
        # Charge the capacitor until our GPIO pin
        # reads HIGH or approximately 1.65 volts
        GPIO.setup(b_pin, GPIO.IN)
        GPIO.setup(a_pin, GPIO.OUT)
        GPIO.output(a_pin, True)
        t1 = time.time()
        while not GPIO.input(b_pin):
            pass
        t2 = time.time()
        # Record the time taken and add to our total for
        # an eventual average calculation
        total = total + (t2 - t1) * 1000000
    # Average our time readings
    reading = total / 100
    # Convert our average time reading to a resistance
    resistance = reading * 6.05 - 939
   
    return resistance
 
# Create a function to convert a resistance reading from our
# thermistor to a temperature in Celsius which we convert to
# Fahrenheit and return to our main loop
def temperature_reading(R):
    B = 3977.0 # Thermistor constant from thermistor datasheet
    R0 = 10000.0 # Resistance of the thermistor being used
    t0 = 273.15 # 0 deg C in K
    t25 = t0 + 25.0 # 25 deg C in K
    # Steinhart-Hart equation
    inv_T = 1/t25 + 1/B * math.log(R/R0)
    T = (1/inv_T - t0) * adjustment_value
    return T # Convert C to F

if __name__ == '__main__': 
	# Main loop
	try:
		while RUNNING:
			# Get the thermistor temperature
			t = temperature_reading(resistance_reading())
	 
			# Print temperature values in real time
			print(t)
	 
			
	 
			# Time interval for taking readings in seconds
			time.sleep(0.1)
	 
	# If CTRL+C is pressed the main loop is broken
	except KeyboardInterrupt:
		RUNNING = False
	 
	 
	# Actions under 'finally' will always be called
	# regardless of what stopped the program
	finally:
		# Stop and cleanup to finish cleanly so the pins
		# are available to be used again
		GPIO.cleanup()

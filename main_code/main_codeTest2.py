# from sense_emu import SenseHat -  use this libaray for emulator on Raspberry Pi
# from sense_hat import SenseHat -  use for actual Sense Hat

import os
import csv
import time
import random
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Test with emulator 
def get_temperature(self):
    return 20 # always 20 degrees C for testing 

def get_humidity(self):
    return 50 # always 50% for testing
        
# Email Configuration
SENDER_EMAIL = "rubuslabs@gmail.com"
APP_PASSWORD = "gbqzuxgifpqxckpu"
RECEIVER_EMAIL = "hurrainghaffar77@gmail.com"

def send_email_alert(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print("📧 Email sent successfully!")
    except Exception as e:
        print("Email failed:", e)

# Initilaise SenseHat
sense = SenseHat()
sense.low_light = True

# LED Colours
green = (0, 255, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
nothing = (0, 0, 0)

# Function to flash signs 
def flash(sign_function, flashes=3, delay=0.4):
    for _ in range(flashes):
        sense.set_pixels(sign_function())
        time.sleep(delay)
        sense.clear()
        time.sleep(delay)

# Red warning sign - indicating soil is too hot 
def red_warning_sign():
    R, Y, O = red, yellow, nothing
    return [
        Y,Y,Y,Y,Y,Y,Y,Y,
        Y,O,O,R,R,O,O,Y,
        Y,O,O,R,R,O,O,Y,
        Y,O,O,R,R,O,O,Y,
        Y,O,O,O,O,O,O,Y,
        Y,O,O,R,R,O,O,Y,
        Y,O,O,R,R,O,O,Y,
        Y,Y,Y,Y,Y,Y,Y,Y,
    ]

# Blue warning sign - indicating soil is too cold
def cold_sign():
    B, O =  blue, nothing
    return [
        B,O,O,B,B,O,O,B,
        O,B,O,B,B,O,B,O,
        O,O,B,B,B,B,O,O,
        B,B,B,B,B,B,B,B,
        B,B,B,B,B,B,B,B,
        O,O,B,B,B,B,O,O,
        O,B,O,B,B,O,B,O,
        B,O,O,B,B,O,O,B,
    ]

# Wet sign - indicating soil is too wet
def wet_sign():
    B, O =  blue, nothing
    return [
        O,O,O,B,O,O,O,O,
        O,O,B,B,B,O,O,O,
        O,B,B,B,B,B,O,O,
        O,B,B,B,B,B,O,O,
        O,B,B,B,B,B,O,O,
        O,O,B,B,B,B,O,O,
        O,O,O,B,B,O,O,O,
        O,O,O,O,O,O,O,O,
    ]

# Green sign - indicating soil is at optimum level 
def optimum():
    G, O = green, nothing
    return [
        O,O,O,O,O,O,O,O,
        O,O,O,G,G,O,O,O,
        O,O,O,G,G,O,O,O,
        O,G,G,G,G,G,G,O,
        O,G,G,G,G,G,G,O,
        O,O,O,G,G,O,O,O,
        O,O,O,G,G,O,O,O,
        O,O,O,O,O,O,O,O,
    ]


# Thresholds for Temperature (°C) and Humidity (%)-  Winter time in Ireland
HOT = 22
COLD = 8
WET = 70
DRY = 40

# Last states
last_state = None
last_email_state = None

# Create csv log to store and save data
def log_to_csv(temperature, humidity):
    file_exists = os.path.isfile("floraguard_log.csv")
    with open("floraguard_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        # Write header only if file doesn't exist
        if not file_exists:
            writer.writerow(["Timestamp", "Temperature (°C)", "Humidity (%)"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
        writer.writerow([timestamp, f"{temperature:.2f}", f"{humidity:.2f}"])
        

# Python analysis - main loop
while True:
    temperature = sense.get_temperature() #  hot & cold
    humidity = sense.get_humidity() # wet & dry
    
    # Defaults
    subject =  None
    body =  None
    
    if temperature < COLD:
        curr_state =  "Cold"
        flash(cold_sign)
        sense.show_message("COLD SOIL", scroll_speed=0.1, text_colour=blue)
        print("ALERT: Soil temperature too low. Move away from windows or cold drafts.")
        subject = "⚠ FloraGuard Alert: Soil Too Cold"
        body = f"""
🌿 FloraGuard Environmental Alert

Hello,

Your plant's soil temperature has fallen below the recommended threshold.

📊 Current Readings:
Temperature: {temperature:.2f} °C
Humidity: {humidity:.2f} %

⚠️ Issue Detected:
The soil is too cold and may slow plant growth.

💡 Recommended Action:
• Move the plant away from windows or drafts
• Consider relocating to a warmer area
• Check room heating levels

This is an automated alert from FloraGuard.

Stay green 🌱  
– Rubus Labs | FloraGuard
"""
        
    elif temperature > HOT:
        curr_state = "Hot"
        flash(red_warning_sign)
        sense.show_message("Hot SOIL", scroll_speed=0.1, text_colour=blue)
        print("ALERT : Soil temperature too high. Please water the plant.")
        subject = "⚠ FloraGuard Alert: Soil Too Hot"
        body = f"""
🌿 FloraGuard Environmental Alert

Hello,

FloraGuard has detected that your plant's soil temperature is above the optimal range.

📊 Current Readings:
Temperature: {temperature:.2f} °C
Humidity: {humidity:.2f} %

⚠️ Issue Detected:
The soil is too warm, which may cause stress to your plant if not addressed.

💡 Recommended Action:
• Water the plant if dry
• Move it away from direct sunlight
• Ensure proper airflow

This is an automated alert from your FloraGuard.

Stay green 🌱  
– Rubus Labs | FloraGuard
"""
            
    elif humidity < DRY:
        curr_state = "Dry"
        flash(red_warning_sign)
        sense.show_message("TOO DRY", scroll_speed=0.1, text_colour=red)
        subject = "⚠ FloraGuard Alert: Soil Too Dry"
        body = body = f"""
🌿 FloraGuard Environmental Alert

Hello,

Your plant's soil humidity is below the recommended threshold.

📊 Current Readings:
Humidity: {humidity:.2f} %
Temperature: {temperature:.2f} °C

⚠️ Issue Detected:
The soil is too dry and may affect plant growth.

💡 Recommended Action:
• Water the plant
• Check the soil moisture regularly
• Ensure proper light and airflow

This is an automated alert from FloraGuard.

Stay green 🌱  
– Rubus Labs | FloraGuard
"""
            
    elif humidity > WET:
         curr_state = "Wet"
         flash(wet_sign)
         sense.show_message("TOO WET", scroll_speed=0.1, text_colour=blue)
         subject = "⚠ FloraGuard Alert: Soil Too Wet"
         body = f"""
🌿 FloraGuard Environmental Alert

Hello,

Your plant's soil humidity is above the recommended threshold.

📊 Current Readings:
Humidity: {humidity:.2f} %
Temperature: {temperature:.2f} °C

⚠️ Issue Detected:
The soil is too wet. Overwatering may harm your plant.

💡 Recommended Action:
• Reduce watering
• Check drainage
• Ensure airflow around the soil

This is an automated alert from FloraGuard.

Stay green 🌱  
– Rubus Labs | FloraGuard
"""
        
    else:
        curr_state = "Good"
        sense.set_pixels(optimum())
        sense.show_message("OPTIMAL", scroll_speed=0.1, text_colour=green)
        print("STATUS 🌱: Soil conditions are optimal.")
        
     # Send email only if state changed
    if last_email_state != curr_state and subject and body:
        send_email_alert(subject, body)
        last_email_state = curr_state

    last_state = curr_state
    log_to_csv(temperature, humidity)
    time.sleep(100)


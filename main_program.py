# FloraGuard Temperature Code & LED Sign Display 
# from sense_emu import SenseHat -  use this libaray for emulator on Raspberry Pi
# from sense_hat import SenseHat 		# use for actual Sense Hat 
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import os
import csv
from datetime import datetime

# -------------------------------
# Fake SenseHat for Testing
# -------------------------------
class SenseHat:
    def __init__(self):
        self.low_light = True

    def get_temperature(self):
        # Simulate changing temperature
        return random.uniform(5, 30)

    def get_humidity(self):
        # Simulate humidity
        return random.uniform(30, 80)

    def set_pixels(self, pixels):
        print("🟩 LED Matrix Updated")

    def clear(self):
        print("⬛ LED Cleared")

    def show_message(self, message, scroll_speed=0.1, text_colour=(255,255,255)):
        print(f"📟 LED Message: {message}")
        time.sleep(1)
        
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
        
sense = SenseHat()
sense.low_light = True

# Colours for LED signs
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
    R = red
    Y = yellow
    O = nothing
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
    B = blue
    O = nothing
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

# Green + sign - indicating soil is at optimum level 
def optimum():
    G = green
    O = nothing
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

# Python analysis 
# Temperature thresholds in °C -  Winter time in Ireland

# Too cold → Below 8°C
# Optimal → 8–22°C
# Too warm → Above 22°C
# Create csv log to store and save data
def log_to_csv(temperature, humidity):

    file_exists = os.path.isfile("floraguard_log.csv")
    
    with open("floraguard_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header only if file doesn't exist
        if not file_exists:
            writer.writerow(["Timestamp", "Temperature (°C)", "Humidity (%)", "Status - "])
       
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, f"{temperature:.2f}", f"{humidity:.2f}"])
        
HOT = 22
COLD = 8
last_state = None # previous state
        
while True:
    temperature = sense.get_temperature() #  hot & cold
    humidity = sense.get_humidity() # wet & dry - not used (yet)
    
    log_to_csv(temperature, humidity)
    
    if temperature > HOT:
        if last_state != "Hot":
            flash(red_warning_sign)
            sense.show_message("HOT SOIL", scroll_speed=0.1, text_colour=red)
            print("ALERT ⚠️: Soil is too warm. Please water the plant.")
            subject = "⚠ FloraGuard Alert: Soil Too Hot"
            body = f"""
🌿 FloraGuard Environmental Alert

Hello,

FloraGuard has detected that your plant's soil temperature is above the optimal range.

📊 Current Readings:
Temperature: {temperature:.2f} °C

⚠️ Issue Detected:
The soil is too warm, which may cause stress to your plant if not addressed.

💡 Recommended Action:
• Water the plant if dry
• Move it away from direct sunlight
• Ensure proper airflow

This is an automated alert from your FloraGuard monitoring system.

Stay green 🌱  
– Rubus Labs | FloraGuard
"""
            send_email_alert(subject, body)
            last_state = "Hot"

    elif temperature < COLD:
        if last_state != "Cold":
            flash(cold_sign)
            sense.show_message("COLD SOIL", scroll_speed=0.1, text_colour=blue)
            print("ALERT ⚠️: Soil is too cold. Move away from windows or cold drafts.")
            subject = "⚠ FloraGuard Alert: Soil Too Cold"
            body = f"""
🌿 FloraGuard Environmental Alert

Hello,

Your plant's soil temperature has fallen below the recommended threshold.

📊 Current Readings:
Temperature: {temperature:.2f} °C

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
            
            send_email_alert(subject, body)
            last_state = "Cold"
            
    else:
        if last_state != "Good":
            sense.set_pixels(optimum())
            sense.show_message("OPTIMAL", scroll_speed=0.1, text_colour=green)
            print("STATUS 🌱: Soil conditions are optimal.")
            subject = "✅ FloraGuard Update: Conditions Restored"
            body = f"""
🌿 FloraGuard Status Update

Good news!

Your plant has returned to optimal environmental conditions.

📊 Current Readings:
Temperature: {temperature:.2f} °C

Everything is within the healthy range.

FloraGuard will continue monitoring and notify you if any changes occur.

Keep growing 🌱  
– Rubus Labs | FloraGuard
"""
            send_email_alert(subject, body)
            last_state = "Good"
            
            time.sleep(300) # checks every 5 seconds

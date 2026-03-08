# from sense_emu import SenseHat  # Uncomment for emulator
from sense_hat import SenseHat  # Use on real Sense HAT

import os
import csv
import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------------------
# Email Configuration
# ------------------------------
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

# ------------------------------
# Initialise SenseHat
# ------------------------------
sense = SenseHat()
sense.low_light = True

# ------------------------------
# LED Colours
# ------------------------------
green = (0, 255, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
nothing = (0, 0, 0)

# ------------------------------
# Flashing function
# ------------------------------
def flash(sign_function, flashes=3, delay=0.4):
    for _ in range(flashes):
        sense.set_pixels(sign_function())
        time.sleep(delay)
        sense.clear()
        time.sleep(delay)

# ------------------------------
# LED Signs
# ------------------------------
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

def cold_sign():
    B, O = blue, nothing
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

def wet_sign():
    B, O = blue, nothing
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

# ------------------------------
# Thresholds for Temperature & Humidity
# ------------------------------
HOT = 22
COLD = 8
WET = 70
DRY = 40

# ------------------------------
# CSV Logging
# ------------------------------
def log_to_csv(temperature, humidity, temp_state, hum_state):
    file_exists = os.path.isfile("temp_hum_log.csv")
    with open("temp_hum_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Temperature (°C)", "Humidity (%)", "Temp Status", "Hum Status"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, f"{temperature:.2f}", f"{humidity:.2f}", temp_state, hum_state])

# ------------------------------
# Main Loop
# ------------------------------
last_email_temp_state = None
last_email_hum_state = None

while True:
    temperature = sense.get_temperature()
    humidity = sense.get_humidity()

    temp_state = None
    hum_state = None

    # ------------------------------
    # Temperature Check
    # ------------------------------
    if temperature < COLD:
        temp_state = "Cold"
        flash(cold_sign)
        sense.show_message("ALERT: Cold", scroll_speed=0.1, text_colour=blue)
        print(f"ALERT: Soil temperature too low: {temperature:.2f}°C")
    elif temperature > HOT:
        temp_state = "Hot"
        flash(red_warning_sign)
        sense.show_message("ALERT: Hot", scroll_speed=0.1, text_colour=red)
        print(f"ALERT: Soil temperature too high: {temperature:.2f}°C")
    else:
        temp_state = "Good"

    # ------------------------------
    # Humidity Check
    # ------------------------------
    if humidity < DRY:
        hum_state = "Dry"
        flash(red_warning_sign)
        sense.show_message("ALERT: Dry", scroll_speed=0.1, text_colour=red)
        print(f"ALERT: Soil is too dry: {humidity:.2f}%")
    elif humidity > WET:
        hum_state = "Wet"
        flash(wet_sign)
        sense.show_message("ALERT: Wet", scroll_speed=0.1, text_colour=blue)
        print(f"ALERT: Soil is too wet: {humidity:.2f}%")
    else:
        hum_state = "Good"

    # ------------------------------
    # Consolidate Issues for Single Email
    # ------------------------------
    issues = []
    if temp_state != "Good":
        issues.append(temp_state)
    if hum_state != "Good":
        issues.append(hum_state)

    if issues and (temp_state != last_email_temp_state or hum_state != last_email_hum_state):
        subject = "⚠ FloraGuard Alert: Soil Issues Detected"
        body = f"""
🌿 FloraGuard Environmental Alert

Current Readings:
Temperature: {temperature:.2f} °C
Humidity: {humidity:.2f} %

⚠️ Issues Detected:
- {"\n- ".join(issues)}

💡 Recommended Actions:
• Follow FloraGuard guidance for the above issues

This is an automated alert from FloraGuard.

Stay green 🌱  
– Rubus Labs | FloraGuard
"""
        send_email_alert(subject, body)
        last_email_temp_state = temp_state
        last_email_hum_state = hum_state

    # ------------------------------
    # Show Optimal if both Good
    # ------------------------------
    if temp_state == "Good" and hum_state == "Good":
        sense.set_pixels(optimum())
        sense.show_message("OPTIMAL", scroll_speed=0.1, text_colour=green)
        print("STATUS 🌱: Soil conditions are optimal.")

    # ------------------------------
    # Log CSV
    # ------------------------------
    log_to_csv(temperature, humidity, temp_state, hum_state)

    # ------------------------------
    # Wait before next reading
    # ------------------------------
    time.sleep(100)
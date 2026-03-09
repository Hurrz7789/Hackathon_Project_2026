# ==============================
# FloraGuard Environmental Monitor
# Rubus Labs
# ==============================

from sense_hat import SenseHat
import os
import csv
import time
import smtplib
from datetime import datetime
from collections import deque
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

        print("Email alert sent")

    except Exception as e:
        print("Email failed:", e)


# ------------------------------
# Sense HAT Setup
# ------------------------------

sense = SenseHat()
sense.low_light = True

green = (0, 255, 0)
red = (255, 0, 0)
black = (0, 0, 0)

# ------------------------------
# Thresholds (FR04)
# ------------------------------

TEMP_LOW = 15
TEMP_HIGH = 28

HUM_LOW = 40
HUM_HIGH = 70

LIGHT_MIN = 50

# ------------------------------
# Moving Average Buffers (FR02)
# ------------------------------

temp_buffer = deque(maxlen=3)
hum_buffer = deque(maxlen=3)
light_buffer = deque(maxlen=3)

# ------------------------------
# CPU Temperature Correction
# ------------------------------


def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    return float(res.replace("temp=", "").replace("'C\n", ""))


# ------------------------------
# CSV Logging (FR03 + NFR07)
# ------------------------------

LOG_FILE = "floraguard_log.csv"


def verify_log_file():

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Timestamp",
                    "Temperature (°C)",
                    "Humidity (%)",
                    "Light (Lux)",
                    "System Status",
                ]
            )


def log_data(temp, hum, light, status):

    verify_log_file()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, f"{temp:.2f}", f"{hum:.2f}", f"{light:.2f}", status])


# ------------------------------
# LED Displays (FR06)
# ------------------------------


def show_green_check():

    check = [
        black, black, black, black, black, black, black, black,
        black, black, black, black, black, green, black, black,
        black, black, black, black, green, black, black, black,
        black, black, black, green, black, black, black, black,
        green, black, green, black, black, black, black, black,
        black, green, black, black, black, black, black, black,
        black, black, black, black, black, black, black, black,
        black, black, black, black, black, black, black, black
    ]

    sense.set_pixels(check)


# ------------------------------
# Email State Control (FR08)
# ------------------------------

email_sent = False


# ------------------------------
# Main Monitoring Loop
# ------------------------------

while True:

    start_time = time.time()

    # --------------------------
    # Sensor Readings (FR01)
    # --------------------------

    raw_temp = sense.get_temperature()
    humidity = sense.get_humidity()
    light = sense.get_colour().clear

    # CPU Heat Correction
    cpu = get_cpu_temp()
    temperature = raw_temp - ((cpu - raw_temp) / 1.5)

    # --------------------------
    # Store in FIFO buffers
    # --------------------------

    temp_buffer.append(temperature)
    hum_buffer.append(humidity)
    light_buffer.append(light)

    # Wait until buffers filled
    if len(temp_buffer) < 3:
        time.sleep(10)
        continue

    # --------------------------
    # Moving Average (FR02)
    # --------------------------

    avg_temp = sum(temp_buffer) / 3
    avg_hum = sum(hum_buffer) / 3
    avg_light = sum(light_buffer) / 3

    # --------------------------
    # Threshold Logic (FR04)
    # --------------------------

    issues = []

    if avg_temp < TEMP_LOW:
        issues.append("TOO COLD")

    if avg_temp > TEMP_HIGH:
        issues.append("TOO HOT")

    if avg_hum < HUM_LOW:
        issues.append("TOO DRY")

    if avg_hum > HUM_HIGH:
        issues.append("TOO HUMID")

    if avg_light < LIGHT_MIN:
        issues.append("LOW LIGHT")

    # --------------------------
    # Determine System State
    # --------------------------

    if len(issues) == 0:

        status = "NORMAL"

        show_green_check()

        email_sent = False

        print("STATUS: Optimal conditions")

    else:

        status = "ANOMALY"

        message = ", ".join(issues)

        sense.show_message(message, text_colour=red, scroll_speed=0.05)

        print("ALERT:", message)

        # --------------------------
        # Send Email (FR08)
        # --------------------------

        if not email_sent:

            subject = "FloraGuard Environmental Alert"

            body = f"""
🌿 FloraGuard has detected environmental issues.

Current Readings:
Temperature: {avg_temp:.2f} °C
Humidity: {avg_hum:.2f} %
Light: {avg_light:.2f} Lux

⚠️ Issues detected:
{message}

💡 Recommended Actions:
• Follow FloraGuard guidance for the above issues

This is an automated alert from FloraGuard.

Stay green 🌱
Rubus Labs | FloraGuard
"""

            send_email_alert(subject, body)

            email_sent = True

    # --------------------------
    # CSV Logging (FR03)
    # --------------------------

    log_data(avg_temp, avg_hum, avg_light, status)

    # --------------------------
    # Performance timing
    # --------------------------

    elapsed = time.time() - start_time

    if elapsed < 10:
        time.sleep(10 - elapsed)
from sense_emu import SenseHat  # Change to sense_hat for the real Pi
import os
import csv
import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. CONFIGURATION
# ==========================================
SENDER_EMAIL = "rubuslabs@gmail.com"
APP_PASSWORD = "gbqzuxgifpqxckpu"
RECEIVER_EMAIL = "hurrainghaffar77@gmail.com"

# Thresholds
HOT = 22
COLD = 8
WET = 70
DRY = 40
DARK = 50  # Light threshold: below 50 Lux is too dark

# ==========================================
# 2. HARDWARE & COLORS
# ==========================================
sense = SenseHat()
sense.low_light = True
sense.color.led_enabled = False # Keeps the sensor's white LED off

# Colors (R, G, B)
G = (0, 255, 0)   # Green
R = (255, 0, 0)   # Red
B = (0, 0, 255)   # Blue
O = (0, 0, 0)     # Off (Black)

# ==========================================
# 3. VISUALS (The Graphics)
# ==========================================
def draw_checkmark():
    """Returns a 64-pixel list for a Green Checkmark."""
    return [
        O,O,O,O,O,O,O,G,
        O,O,O,O,O,O,G,G,
        O,O,O,O,O,G,G,O,
        O,O,O,O,G,G,O,O,
        G,G,O,G,G,O,O,O,
        O,G,G,G,O,O,O,O,
        O,O,G,O,O,O,O,O,
        O,O,O,O,O,O,O,O
    ]

# ==========================================
# 4. UTILITY FUNCTIONS (Email & CSV)
# ==========================================
def send_email_alert(subject, body):
    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = SENDER_EMAIL, RECEIVER_EMAIL, subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print("Email alert sent!")
    except Exception as e:
        print(f"Email failed: {e}")

def log_to_csv(t, h, l, status):
    file_path = "floraguard_log.csv"
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Temp(C)", "Hum(%)", "Light(Lux)", "Status"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, f"{t:.2f}", f"{h:.2f}", f"{l:.2f}", status])

# ==========================================
# 5. MAIN PROGRAM LOOP
# ==========================================
last_email_state = None

print("🌱 FloraGuard System Started...")

while True:
    # A. READ SENSORS
    temp = sense.get_temperature()
    hum = sense.get_humidity()
    # Read the light sensor (Clear channel = Lux)
    red_val, green_val, blue_val, lux = sense.color.colour 
    
    # B. ANALYZE DATA (Build a list of problems)
    problems = []
    
    if temp > HOT: 
        problems.append("HOT")
    elif temp < COLD: 
        problems.append("COLD")
    
    if hum > WET: 
        problems.append("HUMID")
    elif hum < DRY: 
        problems.append("DRY")
    
    if lux < DARK: 
        problems.append("DARK")

    # C. UPDATE DISPLAY
    if not problems:
        # Everything is fine
        current_status = "OPTIMAL"
        sense.set_pixels(draw_checkmark())
    else:
        # Create a single alert string like "TOO HOT TOO DRY"
        current_status = "TOO " + " TOO ".join(problems)
        # Scroll the message in RED to grab attention
        sense.show_message(current_status, scroll_speed=0.08, text_colour=R)

    # D. SEND EMAIL (Only if the status changed)
    if current_status != last_email_state:
        email_subj = f"FloraGuard Status: {current_status}"
        email_body = f"Update: {current_status}\nTemp: {temp:.1f}C\nHum: {hum:.1f}%\nLight: {lux:.1f}Lux"
        send_email_alert(email_subj, email_body)
        last_email_state = current_status

    # E. LOG DATA & WAIT
    log_to_csv(temp, hum, lux, current_status)
    print(f"[{datetime.now().strftime('%H:%M')}] {current_status} | T:{temp:.1f} H:{hum:.1f} L:{lux:.1f}")
    
    time.sleep(10) # 10 seconds for testing/demo
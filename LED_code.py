# FloraGuard Temperature Code & LED Sign Display 
# from sense_emu import SenseHat -  use this libaray for emulator on Raspberry Pi
from sense_hat import SenseHat 		# use for actual Sense Hat 
import time  

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

HOT = 22
COLD = 8
last_state = None # previous state

while True:
    temperature = sense.get_temperature() #  hot & cold
    humidity = sense.get_humidity() # wet & dry - not used (yet)

    if temperature > HOT:
        if last_state != "Hot":
            # Display sign
            flash(red_warning_sign)
            # Display the soil condition & message on LED
            msg = sense.show_message("HOT SOIL", scroll_speed = 0.1, text_colour = red)
            print("ALERT ⚠️: Soil is too warm. Please water the plant.")
            last_state = "Hot"

    elif temperature < COLD:
        if last_state != "Cold":
            # Display sign
            flash(cold_sign)
            # Display the soil condition & message on LED
            msg= sense.show_message("COLD SOIL", scroll_speed = 0.1, text_colour = blue)
            print("ALERT ⚠️: Soil is too cold. Move away from windows or cold drafts.")
            last_state = "Cold"
            
    else:
        if last_state != "Good":
            # Display the soil condition & message on LED
            sense.set_pixels(optimum())
            msg = sense.show_message("OPTIMAL", scroll_speed = 0.1, text_colour = green)
            print("STATUS 🌱: Soil conditions are optimal.")
            last_state = "Good"

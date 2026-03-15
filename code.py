"""CircuitPython firmware for Neo Trinkey M0.
Copy to the CIRCUITPY drive. Controls 4 NeoPixels via USB serial commands.
"""

import math
import time

import board
import neopixel
import usb_cdc

NUM_PIXELS = 4
pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_PIXELS, brightness=0.3, auto_write=False)

ser = usb_cdc.console
ser.timeout = 0

current_anim = "off"
anim_color = (255, 0, 0)
anim_speed = 0.03
step = 0
buf = b""

COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "orange": (255, 80, 0),
    "purple": (128, 0, 255),
    "pink": (255, 50, 50),
    "warm": (255, 150, 50),
}

NO_ARG_ANIMS = ("off", "rainbow", "fire")
COLOR_ANIMS = ("solid", "pulse", "blink", "breathe", "fadeout", "fadein")


def wheel(pos):
    """Map 0-255 to an RGB color, transitioning r-g-b."""
    pos = pos % 256
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def parse_color(s):
    s = s.strip().lower()
    if s in COLORS:
        return COLORS[s]
    parts = s.split(",")
    if len(parts) == 3:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    return None


def respond(msg):
    ser.write(bytes(msg + "\r\n", "utf-8"))


def process_command(line):
    global current_anim, anim_color, anim_speed, step
    parts = line.split(None, 1)
    cmd = parts[0] if parts else ""
    arg = parts[1] if len(parts) > 1 else ""

    if cmd in NO_ARG_ANIMS:
        current_anim = cmd
        step = 0
        respond("OK " + cmd)
    elif cmd in COLOR_ANIMS:
        color = parse_color(arg) if arg else anim_color
        if color:
            anim_color = color
            current_anim = cmd
            step = 0
            respond("OK " + cmd + " " + str(anim_color))
        else:
            respond("ERR bad color: " + arg)
    elif cmd == "brightness":
        try:
            pixels.brightness = float(arg)
            respond("OK brightness " + str(pixels.brightness))
        except Exception:
            respond("ERR bad value")
    elif cmd == "speed":
        try:
            anim_speed = float(arg)
            respond("OK speed " + str(anim_speed))
        except Exception:
            respond("ERR bad value")
    elif cmd == "status":
        respond("anim=" + current_anim + " color=" + str(anim_color) + " speed=" + str(anim_speed))
    elif cmd:
        respond("ERR unknown: " + cmd)


def do_animation():
    global step, current_anim

    if current_anim == "off":
        pixels.fill((0, 0, 0))
    elif current_anim == "solid":
        pixels.fill(anim_color)
    elif current_anim == "rainbow":
        pixels.fill(wheel(step % 256))
        step = (step + 3) % 256
    elif current_anim == "pulse":
        b = (math.sin(step * 0.08) + 1) / 2
        r, g, bl = anim_color
        pixels.fill((int(r * b), int(g * b), int(bl * b)))
        step += 1
    elif current_anim == "blink":
        pixels.fill(anim_color if step % 2 == 0 else (0, 0, 0))
        step = (step + 1) % 2
    elif current_anim == "fire":
        import random

        f = random.randint(100, 255)
        pixels.fill((f, f // 3, 0))
    elif current_anim == "breathe":
        b = (math.sin(step * 0.04) + 1) / 2
        r, g, bl = anim_color
        pixels.fill((int(r * b), int(g * b), int(bl * b)))
        step += 1
    elif current_anim == "fadein":
        steps = 50
        if step < steps:
            b = step / steps
            r, g, bl = anim_color
            pixels.fill((int(r * b), int(g * b), int(bl * b)))
            step += 1
        else:
            pixels.fill(anim_color)
            current_anim = "solid"
    elif current_anim == "fadeout":
        steps = 50
        if step < steps:
            b = 1.0 - (step / steps)
            r, g, bl = anim_color
            pixels.fill((int(r * b), int(g * b), int(bl * b)))
            step += 1
        else:
            pixels.fill((0, 0, 0))
            current_anim = "off"

    pixels.show()


# Main loop: read serial commands (non-blocking), run animation
while True:
    n = ser.in_waiting
    if n > 0:
        buf = buf + ser.read(n)
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            line = line.strip()
            if line:
                process_command(str(line, "utf-8").lower())

    do_animation()
    time.sleep(anim_speed)

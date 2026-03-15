# Neo Trinkey Controller

Control the 4 NeoPixel LEDs on an [Adafruit Neo Trinkey M0](https://www.adafruit.com/product/4870) over USB serial. Includes CircuitPython firmware and a host-side CLI.

## Setup

1. Plug in the Trinkey
2. If CircuitPython isn't installed: double-click the reset button (LEDs go green, `TRINKEYBOOT` drive appears)
3. Run `./install.sh` — flashes firmware, installs the NeoPixel library, and sets up the CLI

## Usage

```
neopixel rainbow          # rainbow cycle
neopixel fire             # flickering fire
neopixel pulse blue       # pulsing blue
neopixel breathe warm     # slow warm breathing
neopixel solid cyan       # static cyan
neopixel blink red        # blinking red
neopixel brightness 0.5   # half brightness
neopixel speed 0.05       # slower animation
neopixel status           # current state
neopixel off
```

Colors: `red` `green` `blue` `white` `yellow` `cyan` `magenta` `orange` `purple` `pink` `warm` or `r,g,b` (e.g. `255,128,0`)

## How it works

`code.py` runs on the Trinkey via CircuitPython. It drives the NeoPixels and reads commands from USB serial (`/dev/ttyACM0`, 115200 baud). `neopixel-cli` is a thin Python wrapper that sends commands and prints responses.

```
neopixel-cli  ──USB serial──>  code.py (CircuitPython)  ──>  4x NeoPixels
```

Commands are newline-terminated, responses prefixed with `OK` or `ERR`:

```
> rainbow
< OK rainbow

> solid 255,0,128
< OK solid (255, 0, 128)
```

## Adding animations

Add a branch in `do_animation()` in `code.py`:

```python
elif current_anim == "myeffect":
    pixels.fill((step % 256, 0, 0))
    step += 1
```

Then add `"myeffect"` to the command list in `process_command()`. Copy the updated file to the CIRCUITPY drive — it auto-reloads.

## Troubleshooting

If the Trinkey is unresponsive after a firmware crash (stuck in REPL), reset it before redeploying:

```bash
python3 -c "import serial; s=serial.Serial('/dev/ttyACM0', 115200); s.write(b'\x03\x04'); s.close()"
```

This sends ctrl-C (interrupt) + ctrl-D (soft reboot). CircuitPython will reload `code.py` from the CIRCUITPY drive.

## CircuitPython gotchas

This targets CircuitPython 10.x on SAMD21, which differs from CPython:

- No `bytes.decode()` — use `str(b, "utf-8")`
- No `str.encode()` — use `bytes(s, "utf-8")`
- Serial via `usb_cdc.console` with `.in_waiting` / `.read(n)`

## Requirements

- **Host:** Python 3, pyserial (`python3-serial` on Debian/Ubuntu)
- **Trinkey:** CircuitPython 10.x, `neopixel` library (both handled by `install.sh`)

## License

MIT

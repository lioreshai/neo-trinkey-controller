#!/bin/bash
set -e

echo "=== Neo Trinkey Controller Setup ==="

# Install host dependency
echo "Installing pyserial..."
sudo apt install -y python3-serial

# Flash CircuitPython if in bootloader mode
if mount | grep -q TRINKEYBOOT; then
    echo "TRINKEYBOOT detected, flashing CircuitPython..."
    UF2="https://downloads.circuitpython.org/bin/neopixel_trinkey_m0/en_US/adafruit-circuitpython-neopixel_trinkey_m0-en_US-10.1.4.uf2"
    curl -sL "$UF2" -o /tmp/circuitpython.uf2
    BOOT=$(mount | grep TRINKEYBOOT | awk '{print $3}')
    cp /tmp/circuitpython.uf2 "$BOOT/"
    echo "Waiting for reboot..."
    sleep 10
fi

# Find CIRCUITPY drive
CIRCUITPY=""
for path in /media/*/CIRCUITPY /run/media/*/CIRCUITPY; do
    [ -d "$path" ] && CIRCUITPY="$path" && break
done

if [ -z "$CIRCUITPY" ]; then
    echo "CIRCUITPY drive not found."
    echo "If CircuitPython isn't installed: double-click the reset button, then re-run."
    exit 1
fi
echo "Found CIRCUITPY at $CIRCUITPY"

# Install neopixel library via circup
if ! command -v circup &>/dev/null; then
    pip install --user --break-system-packages circup 2>/dev/null || pip install --user circup
fi
CIRCUP=$(command -v circup || echo "$HOME/.local/bin/circup")
"$CIRCUP" --path "$CIRCUITPY" install neopixel

# Deploy firmware
cp code.py "$CIRCUITPY/code.py"
echo "Firmware deployed."

# Install CLI
sudo cp neopixel-cli /usr/local/bin/neopixel
sudo chmod +x /usr/local/bin/neopixel

# Serial access
if ! groups | grep -q dialout; then
    sudo usermod -aG dialout "$USER"
    echo "Added $USER to dialout group (re-login to take effect)"
fi

echo "Done. Test with: neopixel rainbow"

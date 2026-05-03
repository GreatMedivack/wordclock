#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export CLOCK_DIR="$SCRIPT_DIR"
export LOG="/dev/stdout"

echo "=== Word Clock manual install ==="

echo "Enabling SPI and I2C..."
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

sudo -E bash "$SCRIPT_DIR/deploy/install-deps.sh"

echo "Installing systemd service..."
sudo cp "$SCRIPT_DIR/wordclock.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wordclock.service

echo ""
echo "Done! Start the clock with:"
echo "  sudo systemctl start wordclock"
echo ""
echo "Or run manually:"
echo "  sudo python3 $SCRIPT_DIR/clock.py"

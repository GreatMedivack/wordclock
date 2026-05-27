#!/bin/bash
set -euo pipefail

CLOCK_DIR="${CLOCK_DIR:-/home/pi/clock}"
LOG="${LOG:-/dev/stdout}"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

log "Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3-pip python3-pil libopenjp2-7 git

log "Installing Waveshare e-Paper library..."
TMPDIR=$(mktemp -d)
git clone --depth 1 https://github.com/waveshare/e-Paper.git "$TMPDIR/e-Paper"
cd "$TMPDIR/e-Paper/RaspberryPi_JetsonNano/python"
python3 setup.py install --quiet
cd /
rm -rf "$TMPDIR"

log "Installing Python dependencies..."
pip3 install --break-system-packages -q -r "$CLOCK_DIR/requirements.txt"

log "Dependencies installed successfully"

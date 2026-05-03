#!/bin/bash
set -euo pipefail

CLOCK_DIR="/home/pi/clock"
LOG="$CLOCK_DIR/firstboot.log"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

log "=== Word Clock first boot setup started ==="

log "Waiting for network..."
for i in $(seq 1 30); do
    if ping -c1 -W2 google.com >/dev/null 2>&1; then
        log "Network is up"
        break
    fi
    if [ "$i" -eq 30 ]; then
        log "ERROR: No network after 60s, aborting"
        exit 1
    fi
    sleep 2
done

export CLOCK_DIR LOG
source "$CLOCK_DIR/deploy/install-deps.sh"

log "Enabling wordclock service..."
systemctl enable wordclock.service
systemctl start wordclock.service

log "Disabling firstboot service (one-shot done)..."
systemctl disable wordclock-firstboot.service

log "=== First boot setup complete ==="

#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TARGET_USER="pi"
CLOCK_DIR="/home/$TARGET_USER/clock"

usage() {
    echo "Usage: sudo $0 <sd-mount-base>"
    echo ""
    echo "Prepares a freshly-flashed Raspberry Pi OS SD card for the word clock."
    echo "Run this AFTER flashing with Raspberry Pi Imager."
    echo ""
    echo "  <sd-mount-base>  Path where SD partitions are mounted."
    echo "                   E.g. /media/\$USER or /mnt"
    echo ""
    echo "The script looks for boot (bootfs) and root (rootfs) partitions"
    echo "under the given path."
    exit 1
}

die() { echo "ERROR: $*" >&2; exit 1; }

[ $# -eq 1 ] || usage
[ "$(id -u)" -eq 0 ] || die "Must run as root (sudo)"

BASE="$1"

# --- Detect boot partition ---
BOOT=""
for candidate in "$BASE/bootfs" "$BASE/boot" "$BASE/boot/firmware"; do
    if [ -f "$candidate/cmdline.txt" ] || [ -f "$candidate/config.txt" ]; then
        BOOT="$candidate"
        break
    fi
done
[ -n "$BOOT" ] || die "Cannot find boot partition under $BASE (looked for cmdline.txt/config.txt)"

# --- Detect rootfs partition ---
ROOTFS=""
for candidate in "$BASE/rootfs" "$BASE/root"; do
    if [ -d "$candidate/etc" ] && [ -d "$candidate/usr" ]; then
        ROOTFS="$candidate"
        break
    fi
done
[ -n "$ROOTFS" ] || die "Cannot find rootfs partition under $BASE (looked for /etc)"

echo "Boot partition: $BOOT"
echo "Root partition: $ROOTFS"
echo ""

# --- Configure boot/config.txt ---
echo "=== Configuring config.txt ==="
CONFIG="$BOOT/config.txt"

append_if_missing() {
    if ! grep -q "^$1" "$CONFIG"; then
        echo "$1" >> "$CONFIG"
        echo "  Added: $1"
    else
        echo "  Already set: $1"
    fi
}

append_if_missing "dtparam=spi=on"
append_if_missing "dtparam=i2c_arm=on"
append_if_missing "gpu_mem=16"
append_if_missing "dtoverlay=disable-bt"

# --- Copy application files ---
echo ""
echo "=== Copying application to $ROOTFS$CLOCK_DIR ==="
mkdir -p "$ROOTFS$CLOCK_DIR"

cp "$PROJECT_DIR/clock.py" "$ROOTFS$CLOCK_DIR/"
cp "$PROJECT_DIR/renderer.py" "$ROOTFS$CLOCK_DIR/"
cp "$PROJECT_DIR/epd_driver.py" "$ROOTFS$CLOCK_DIR/"
cp "$PROJECT_DIR/time_source.py" "$ROOTFS$CLOCK_DIR/"
cp "$PROJECT_DIR/requirements.txt" "$ROOTFS$CLOCK_DIR/"

mkdir -p "$ROOTFS$CLOCK_DIR/fonts"
cp "$PROJECT_DIR/fonts/"*.ttf "$ROOTFS$CLOCK_DIR/fonts/"

mkdir -p "$ROOTFS$CLOCK_DIR/deploy"
cp "$PROJECT_DIR/deploy/install-deps.sh" "$ROOTFS$CLOCK_DIR/deploy/"
cp "$PROJECT_DIR/deploy/firstboot.sh" "$ROOTFS$CLOCK_DIR/deploy/"
chmod +x "$ROOTFS$CLOCK_DIR/deploy/install-deps.sh"
chmod +x "$ROOTFS$CLOCK_DIR/deploy/firstboot.sh"

# --- Detect target user from rootfs ---
if [ -d "$ROOTFS/home/$TARGET_USER" ]; then
    echo "  Target user: $TARGET_USER"
else
    FOUND_USER=$(ls "$ROOTFS/home/" 2>/dev/null | head -1)
    if [ -n "$FOUND_USER" ]; then
        echo "  User '$TARGET_USER' not found, using '$FOUND_USER'"
        TARGET_USER="$FOUND_USER"
        NEW_CLOCK_DIR="/home/$TARGET_USER/clock"
        mv "$ROOTFS$CLOCK_DIR" "$ROOTFS$NEW_CLOCK_DIR" 2>/dev/null || true
        CLOCK_DIR="$NEW_CLOCK_DIR"
    fi
fi

# --- Install systemd services ---
echo ""
echo "=== Installing systemd services ==="

cat > "$ROOTFS/etc/systemd/system/wordclock.service" <<EOF
[Unit]
Description=Word Clock E-Ink Display
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $CLOCK_DIR/clock.py
WorkingDirectory=$CLOCK_DIR
Restart=on-failure
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF
echo "  Installed wordclock.service"

cat > "$ROOTFS/etc/systemd/system/wordclock-firstboot.service" <<EOF
[Unit]
Description=Word Clock First Boot Setup
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=$CLOCK_DIR/deploy/firstboot.sh
RemainAfterExit=false
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target
EOF
echo "  Installed wordclock-firstboot.service"

# Enable firstboot service (create symlink manually since systemctl won't work on mounted fs)
mkdir -p "$ROOTFS/etc/systemd/system/multi-user.target.wants"
ln -sf /etc/systemd/system/wordclock-firstboot.service \
    "$ROOTFS/etc/systemd/system/multi-user.target.wants/wordclock-firstboot.service"
echo "  Enabled wordclock-firstboot.service"

# --- Fix ownership ---
# Get UID/GID of target user from rootfs passwd
TARGET_UID=$(grep "^$TARGET_USER:" "$ROOTFS/etc/passwd" | cut -d: -f3)
TARGET_GID=$(grep "^$TARGET_USER:" "$ROOTFS/etc/passwd" | cut -d: -f4)
if [ -n "$TARGET_UID" ] && [ -n "$TARGET_GID" ]; then
    chown -R "$TARGET_UID:$TARGET_GID" "$ROOTFS$CLOCK_DIR"
    echo "  Set ownership to $TARGET_USER ($TARGET_UID:$TARGET_GID)"
fi

echo ""
echo "=== SD card is ready ==="
echo ""
echo "Next steps:"
echo "  1. Unmount SD card"
echo "  2. Insert into Pi Zero W"
echo "  3. Power on — first boot will install deps and start the clock"
echo "  4. SSH in after ~5 min: ssh $TARGET_USER@<pi-ip>"
echo "  5. Check: systemctl status wordclock"
echo "  6. Log:   cat $CLOCK_DIR/firstboot.log"

#!/usr/bin/env bash
# Removes the system-wide Delete When Unzip install.
set -e

if [ "$EUID" -ne 0 ]; then
    echo "Run this with sudo: sudo ./uninstall.sh"
    exit 1
fi

rm -rf /usr/local/share/delete-when-unzip
rm -f /usr/local/bin/delete-when-unzip
rm -f /usr/local/bin/delete-when-unzip-cli
rm -f /usr/share/applications/delete-when-unzip.desktop
rm -f /usr/share/icons/hicolor/32x32/apps/delete-when-unzip.png

echo "Uninstalled."

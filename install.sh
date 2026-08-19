#!/usr/bin/env bash
# Installs Delete When Unzip system-wide (no venv).

if [ "$EUID" -ne 0 ]; then
    echo "Run this with sudo: sudo ./install.sh"
    exit 1
fi

SYSTEM_DEPS_OK=1

echo "Installing system dependencies..."
if command -v apt >/dev/null; then
    if apt update && apt install -y python3 python3-tk python3-pip libarchive-dev unrar; then
        echo "System packages installed via apt."
    else
        echo "WARNING: 'apt install' failed. Some packages may be missing or renamed on your system." >&2
        SYSTEM_DEPS_OK=0
    fi

elif command -v dnf >/dev/null; then
    # unrar is not in Fedora's default repos - it lives in RPM Fusion (nonfree)
    if ! rpm -q rpmfusion-nonfree-release >/dev/null 2>&1; then
        if ! dnf install -y "https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm"; then
            echo "WARNING: could not enable RPM Fusion (needed for unrar). Continuing without it." >&2
        fi
    fi
    if dnf install -y python3 python3-tkinter python3-pip libarchive unrar; then
        echo "System packages installed via dnf."
    else
        echo "WARNING: 'dnf install' failed. Some packages may be missing or renamed on your system." >&2
        SYSTEM_DEPS_OK=0
    fi

else
    echo "WARNING: unrecognized package manager (not apt or dnf)." >&2
    SYSTEM_DEPS_OK=0
fi

if [ "$SYSTEM_DEPS_OK" -eq 0 ]; then
    echo ""
    echo "Could not confirm system packages installed automatically."
    echo "Please install these manually via your distro's package manager:"
    echo "  - python3, python3-tk (tkinter) -- needed for the GUI"
    echo "  - libarchive -- needed for RAR/other archive support"
    echo "  - unrar -- needed for segmented RAR volumes"
    echo ""
    echo "Continuing with the parts this script CAN still do (Python packages, app files)..."
    echo ""
fi

echo "Installing Python packages via pip..."
if pip3 install --break-system-packages stream_unzip==0.0.88 libarchive-c==5.1; then
    echo "Python packages installed."
else
    echo "ERROR: pip install failed. The app will not run until stream_unzip and libarchive-c are installed." >&2
fi

APP_DIR="/usr/local/share/delete-when-unzip"
echo "Copying application files to $APP_DIR..."
mkdir -p "$APP_DIR"
cp ./*.py "$APP_DIR/"
cp app_icon.png "$APP_DIR/"

echo "Installing launchers..."
cat > /usr/local/bin/delete-when-unzip << EOF
#!/usr/bin/env bash
exec python3 $APP_DIR/app.py "\$@"
EOF
chmod +x /usr/local/bin/delete-when-unzip

cat > /usr/local/bin/delete-when-unzip-cli << EOF
#!/usr/bin/env bash
exec python3 $APP_DIR/delete_when_unzip_cli.py "\$@"
EOF
chmod +x /usr/local/bin/delete-when-unzip-cli

echo "Installing desktop entry and icon..."
mkdir -p /usr/share/applications
cp delete-when-unzip.desktop /usr/share/applications/delete-when-unzip.desktop
mkdir -p /usr/share/icons/hicolor/32x32/apps
cp app_icon.png /usr/share/icons/hicolor/32x32/apps/delete-when-unzip.png

echo ""
if [ "$SYSTEM_DEPS_OK" -eq 1 ]; then
    echo "Install complete. Launch with: delete-when-unzip"
else
    echo "Partial install complete. App files are in place, but install the missing"
    echo "system packages listed above before running: delete-when-unzip"
fi

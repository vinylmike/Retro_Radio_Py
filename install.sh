#!/bin/bash

# Configuration
REPO_URL="https://github.com/vinylmike/Retro_Radio_Py.git"
APP_DIR="/home/vinylmike/Retro_Radio_Py"
SERVICE_NAME="retro_radio_py"

echo "📦 Installing Retro_Radio_Py..."

# Update and install system packages
sudo apt update
sudo apt install -y python3 python3-pip git mpv

# Clone or pull the latest version
if [ -d "$APP_DIR" ]; then
  echo "📁 Repo exists. Pulling latest..."
  cd "$APP_DIR" && git pull
else
  echo "📁 Cloning repo..."
  git clone "$REPO_URL" "$APP_DIR"
fi

# Install Python dependencies
cd "$APP_DIR"
pip3 install -r requirements.txt || pip3 install flask

# Create systemd service
echo "🛠 Creating systemd service..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Retro Radio Py
After=network.target

[Service]
ExecStart=/usr/bin/python3 $APP_DIR/main.py
WorkingDirectory=$APP_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "✅ Installation complete! Flask app is running on port 5000."
echo "🔁 Reboot the Pi or run: sudo systemctl restart $SERVICE_NAME"

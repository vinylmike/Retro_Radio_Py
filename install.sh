#!/bin/bash

echo "🔧 Installing dependencies..."
pip3 install flask
sudo apt-get update
sudo apt-get install -y mpv

echo "⚙️ Setting up systemd service..."
sudo cp retro_radio_py.service /etc/systemd/system/retro_radio_py.service

echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable retro_radio_py
sudo systemctl restart retro_radio_py

echo "✅ Install complete. Check status:"
sudo systemctl status retro_radio_py

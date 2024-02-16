#!/bin/bash
# Setup script
echo "Update and install Python"
sudo apt update && sudo apt upgrade -y
sudo apt install python3-full 
echo "Setup venv and install modules"
mkdir env && python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install --upgrade pyserial meshtastic
echo "Install raspi-blinka"
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/raspi-blinka.py
python3 raspi-blinka.py

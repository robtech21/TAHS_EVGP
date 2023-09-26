# TAHS_EVGP
All tools and files used for the TAHS data analytics program for the Shenandoah Valley EV Grand Prix

# Disclaimers

* This is fairly incomplete so far, I still need to write a completely "coherent" guide for setting up systems for both transmit and receive.
* The original `data_monitor.py` file was meant for serial reception and is legacy, please use `data_monitor_mesh.py`.

# Setup

How to setup the data system. For the time being I will assume that the Meshtastic Tx and Rx devices are setup correctly.

## Receiver

(Assuming you're using Windows)
TODO: add `requirements.txt` for pip

* Plug in the receiver device to your device
* Open your terminal go into the `receive` folder
* Run `py -m http.server -b 127.0.0.1`
* Open the address in your web browser by CTRL+clicking it
* Open another terminal and go into the same folder
* Run `py data_monitor_mesh.py`

If all goes correctly, the receiver should be listed on startup as a default if you have no other devices connected. Press enter to start logging from the mesh device.

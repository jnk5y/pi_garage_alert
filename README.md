Pi Garage Manager
===============

Docker container with a Raspberry Pi Python script to email or send an SMS (IFTTT) if a garage door is left open. It can also trigger the garage door to open/close.

QUICK START
---------------
BASIC RASPBERRY PI SETUP
Equipment required
* Raspberry Pi model A or B
* 2GB or larger SD card
* Magnetic sensor (e.g. https://www.amazon.com/uxcell-Stainless-Security-Magnetic-Contact/dp/B005DJLILI/ref=sr_1_10)*
* USB wifi adapter (if not using Ethernet)
* USB power supply for RPi (https://www.amazon.com/Edimax-EW-7811Un-150Mbps-Raspberry-Supports/dp/B003MTTJOY/ref=sr_1_4)
* 2 channel relay (https://www.amazon.com/SunFounder-Channel-Optocoupler-Expansion-Raspberry/dp/B00E0NTPP4/ref=sr_1_1)
* Female to female jumper cables (https://www.amazon.com/40pcs-Female-2-54mm-Jumper-2x40pcs/dp/B00GSE2S98/ref=sr_1_4)

RASPBERRY PI INITIAL SETUP
* Follow the guide at http://elinux.org/RPi_Easy_SD_Card_Setup to write the Raspbian image to the SD card.
* Boot the RPi and at raspi-config, expand the filesystem, set the "pi" account password, and enable SSH.
* Reboot the Raspberry Pi
* Edit /etc/wpa_supplicant/wpa_supplicant.conf and configure the RPi to connect to your wifi network.
* Run `sudo apt update && sudo apt upgrade`
* Run `sudo apt install git`

PI GARAGE MANAGER WIRING DIAGRAMS
* Check out the wiki for the wiring diagrams - https://github.com/jnk5y/pi_garage_manager/wiki
	
RUNNING PI_GARAGE_MANAGER
* Edit the pi_garage_manager_config.py file
	* Modify the alert section to suit your alerting needs
	* Add your firebase key
* type 'docker build -t pi_garage_manager_image .' in the folder with the Dockerfile to create the docker image
* type 'docker run -d --restart unless-stopped --device /dev/ttyAMA0:/dev/ttyAMA0 --device /dev/mem:/dev/mem --privileged --name pi_garage_manager -p 6000:6000 pi_garage_manager_image' to run the container.
* At this point, the Pi Garage Manager software should be running. You can use the garage_trigger.py script to send commands to the service to open/close the garage door.

Thanks to:
* Shane Rowley - https://github.com/smrowley

* Rich Lynch - https://www.richlynch.com/2013/07/27/pi_garage_alert_1/

* Driscocity's Idiot's Guide - http://www.driscocity.com/idiots-guide-to-a-raspberry-pi-garage-door-opener/

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
	
RUNNING PI_GARAGE_MANAGER
* sudo apt-get install python-setuptools python-dev libffi-dev
* sudo easy_install pip
* sudo pip install requests
* sudo pip install requests[security]
* Optional email configuration
	* Configure postfix to send mail using Google SMTP, or your ISP's SMTP server
	* This guide shows how to setup Google SMTP - https://www.linode.com/docs/email/postfix/configure-postfix-to-send-mail-using-gmail-and-google-apps-on-debian-or-ubuntu
* Edit the etc/pi_garage_manager_config.py file
	* Modify the alert section to suit your alerting needs
	* If you want an email alert add your email information setup from above
	* if you want an IFTTT alert (notification or SMS) add your IFTTT key
* Run the install.sh script `sudo bash ./install.sh`
	* The install script will copy bin/pi_garage_manager.py to /usr/local/sbin, etc/pi_garage_manager_config.py to /usr/local/etc, init.d/pi_garage_manager to /etc/init.d and make pi_garage_manager.py start on startup
* To run the pi_garage_manager service run `sudo sudo service pi_garage_manager start`
* At this point, the Pi Garage Manager software should be running. You can view its log in /var/log/pi_garage_manager.log. You can use the pi_garage_trigger.py script found in bin/ to send commands to the service to open/close the garage door.

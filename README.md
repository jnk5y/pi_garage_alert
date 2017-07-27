Pi Garage Alert
===============

Docker container with a Raspberry Pi Python script to email or send an SMS (IFTTT) if a garage door is left open. It can also trigger the garage door to open/close.

QUICK START
---------------
BASIC RASPBERRY PI SETUP
1. Equipment required
	1. Raspberry Pi model A or B
	1. 2GB or larger SD card
	1. Magnetic sensor (e.g. https://www.amazon.com/uxcell-Stainless-Security-Magnetic-Contact/dp/B005DJLILI/ref=sr_1_10)
	1. USB wifi adapter (if not using Ethernet)
	1. USB power supply for RPi (https://www.amazon.com/Edimax-EW-7811Un-150Mbps-Raspberry-Supports/dp/B003MTTJOY/ref=sr_1_4)
	1. 2 channel relay (https://www.amazon.com/SunFounder-Channel-Optocoupler-Expansion-Raspberry/dp/B00E0NTPP4/ref=sr_1_1)
1. Raspberry Pi initial setup
	1. Follow the guide at http://elinux.org/RPi_Easy_SD_Card_Setup to write the Raspbian image to the SD card.
 	1. Boot the RPi and at raspi-config, expand the filesystem, set the "pi" account password, and enable SSH.
  	1. Reboot the Raspberry Pi
  	1. Edit /etc/wpa_supplicant/wpa_supplicant.conf and configure the RPi to connect to your wifi network.
  	1. Run `sudo apt update && sudo apt upgrade`
  	1. Run `sudo apt install git`
<br><br>
PI_GARAGE_ALERT SETUP USING DOCKER
1. git clone https://github.com/jnk5y/pi_garage_alert.git
1. From the pi_garage_alert directory run `docker build -t garage-listener .`
1. Then run `docker run --device /dev/ttyAMA0:/dev/ttyAMA0 --device /dev/mem:/dev/mem --privileged --name garage-container garage-listener`
<br><br>
RUNNING PI_GARAGE_ALERT MANUALLY
1. sudo apt-get install python-setuptools python-dev libffi-dev<br>
sudo easy_install pip<br>
sudo pip install requests<br>
sudo pip install requests[security]<br>
1. Optional email configuration
	1. Configure postfix to send mail using Google SMTP, or your ISP's SMTP server
1. Edit the etc/pi_garage_alert_config.py file
  1. Modify the garage door section to suit your alert needs
  1. If you want an email alert add your email information
  1. If you want an IFTTT alert (notification or SMS) add your IFTTT key
1. Copy bin/pi_garage_alert.py to /usr/local/sbin
1. Copy etc/pi_garage_alert_config.py to /usr/local/etc.
1. Copy init.d/pi_garage_alert to /etc/init.d
1. Configure and start the service with<br>
sudo update-rc.d pi_garage_alert defaults<br>
sudo service pi_garage_alert start<br>
1. At this point, the Pi Garage Alert software should be running. You can view its log in /var/log/pi_garage_alert.log

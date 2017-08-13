#!/usr/bin/env python
""" Pi Garage Manager

Author: Richard L. Lynch <rich@richlynch.com>

Description: Emails, tweets, or sends an SMS if a garage door is left open
too long.

Learn more at http://www.richlynch.com/code/pi_garage_alert
"""

##############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 Richard L. Lynch <rich@richlynch.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
##############################################################################

import time
from time import strftime
from datetime import datetime
import subprocess
import re
import sys
import json
import logging
from datetime import timedelta
import smtplib
import ssl
import traceback
from email.mime.text import MIMEText
import socket
import multiprocessing
import threading
import requests
import httplib2
import RPi.GPIO as GPIO

sys.path.append('/usr/local/etc')
import pi_garage_manager_config as cfg

##############################################################################
# Email support
##############################################################################

class Email(object):
    """Class to send emails"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def send_email(self, recipient, subject, msg):
        """Sends an email to the specified email address.

        Args:
            recipient: Email address to send to.
            subject: Email subject.
            msg: Body of email to send.
        """
        self.logger.info("Sending email to %s: subject = \"%s\", message = \"%s\"", recipient, subject, msg)

        msg = MIMEText(msg)
        msg['Subject'] = subject
        msg['To'] = recipient
        msg['From'] = cfg.EMAIL_FROM
        msg['X-Priority'] = cfg.EMAIL_PRIORITY

        try:
            mail = smtplib.SMTP(cfg.SMTP_SERVER, cfg.SMTP_PORT)
            if cfg.SMTP_USER != '' and cfg.SMTP_PASS != '':
                mail.login(cfg.SMTP_USER, cfg.SMTP_PASS)
            mail.sendmail(cfg.EMAIL_FROM, recipient, msg.as_string())
            mail.quit()
        except:
            self.logger.error("Exception sending email: %s", sys.exc_info()[0])

##############################################################################
# IFTTT support using Maker Channel (https://ifttt.com/maker)
##############################################################################

class IFTTT(object):
    """Class to send IFTTT triggers using the Maker Channel"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def send_trigger(self, event, value1, value2, value3):
        """Send an IFTTT event using the maker channel.

        Get the key by following the URL at https://ifttt.com/services/maker/settings

        Args:
            event: Event name
            value1, value2, value3: Optional data to supply to IFTTT.
        """
        self.logger.info("Sending IFTTT event \"%s\": value1 = \"%s\", value2 = \"%s\", value3 = \"%s\"", event, value1, value2, value3)

        headers = {'Content-type': 'application/json'}
        payload = {'value1': value1, 'value2': value2, 'value3': value3}
        try:
            requests.post("https://maker.ifttt.com/trigger/%s/with/key/%s" % (event, cfg.IFTTT_KEY), headers=headers, data=json.dumps(payload))
        except:
            self.logger.error("Exception sending IFTTT event: %s", sys.exc_info()[0])

##############################################################################
# Garage Door Sensor support
##############################################################################

def get_garage_door_state(pin):
    """Returns the state of the garage door on the specified pin as a string

    Args:
        pin: GPIO pin number.
    """
    if GPIO.input(pin): # pylint: disable=no-member
        state = 'open'
    else:
        state = 'closed'

    return state

def get_uptime():
    """Returns the uptime of the RPi as a string
    """
    with open('/proc/uptime', 'r') as uptime_file:
        uptime_seconds = int(float(uptime_file.readline().split()[0]))
        uptime_string = str(timedelta(seconds=uptime_seconds))
    return uptime_string

##############################################################################
# Trigger garage door to open or close
##############################################################################

def doorTriggerLoop():

    state = get_garage_door_state(cfg.PIN)
    status = cfg.HOMEAWAY

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("192.168.86.9", 6000))
    sock.listen(1)

    while True:
        (conn, address) = sock.accept()
        received = conn.recv(1024)
        response = 'unknown command'
        trigger = False

        if received == 'trigger':
            trigger = True
            if state == 'open':
                response = 'closing garage door'
            else:
                response = 'opening garage door'
        elif received == 'open':
            if state == 'open':
                response = 'garage door already open'
            else:
                response = 'opening garage door'
                trigger = True
        elif received == 'close':
            if state == 'open':
                response = 'closing garage door'
                trigger = True
            else:
                response = 'garage door alredy closed'
        elif received == 'state':
            response = 'the garage door is ' + state
        elif received == 'home':
            cfg.HOMEAWAY = 'home'
            response = 'alert status set to HOME'
        elif received == 'away':
            cfg.HOMEAWAY = 'away'
            response = 'alert status set to AWAY'

        conn.send_bytes(response)
        print 'Received command to ' + received + ' the garage door. Response was ' + response

        if trigger:
            GPIO.output(26, GPIO.LOW)
            print 'Door triggered'
	    time.sleep(3)
	    GPIO.output(26, GPIO.HIGH)

        trigger = False
        time.sleep(1)

    conn.close()
    listener.close()

##############################################################################
# Logging and alerts
##############################################################################

def send_alerts(logger, alert_senders, recipients, subject, msg, state, time_in_state):
    """Send subject and msg to specified recipients

    Args:
        recipients: An array of strings of the form type:address
        subject: Subject of the alert
        msg: Body of the alert
        state: The state of the door
    """
    for recipient in recipients:
        if recipient[:6] == 'email:':
            alert_senders['Email'].send_email(recipient[6:], subject, msg)
        elif recipient[:6] == 'ifttt:':
            alert_senders['IFTTT'].send_trigger(recipient[6:], subject, state, '%d' % (time_in_state))
        else:
            logger.error("Unrecognized recipient type: %s", recipient)

##############################################################################
# Misc support
##############################################################################

def truncate(input_str, length):
    """Truncate string to specified length

    Args:
        input_str: String to truncate
        length: Maximum length of output string
    """
    if len(input_str) < (length - 3):
        return input_str

    return input_str[:(length - 3)] + '...'

def format_duration(duration_sec):
    """Format a duration into a human friendly string"""
    days, remainder = divmod(duration_sec, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    ret = ''
    if days > 1:
        ret += "%d days " % (days)
    elif days == 1:
        ret += "%d day " % (days)

    if hours > 1:
        ret += "%d hours " % (hours)
    elif hours == 1:
        ret += "%d hour " % (hours)

    if minutes > 1:
        ret += "%d minutes" % (minutes)
    if minutes == 1:
        ret += "%d minute" % (minutes)

    if ret == '':
        ret += "%d seconds" % (seconds)

    return ret


##############################################################################
# Main functionality
##############################################################################
class PiGarageAlert(object):
    """Class with main function of Pi Garage Alert"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def main(self):
        """Main functionality
        """

        try:
            # Set up logging
            log_fmt = '%(asctime)-15s %(levelname)-8s %(message)s'
            log_level = logging.INFO

            if sys.stdout.isatty():
                # Connected to a real terminal - log to stdout
                logging.basicConfig(format=log_fmt, level=log_level)
            else:
                # Background mode - log to file
                logging.basicConfig(format=log_fmt, level=log_level, filename=cfg.LOG_FILENAME)

            # Banner
            self.logger.info("==========================================================")
            self.logger.info("Pi Garage Manager Starting")

            # Use Raspberry Pi board pin numbers
            GPIO.setmode(GPIO.BOARD)
            # Configure the sensor pins as inputs with pull up resistors
            self.logger.info("Configuring pin %d and 26 for \"%s\"", cfg.PIN, cfg.NAME)
            GPIO.setup(cfg.PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
 
	    # Configure the sensor pin for the relay to open and close the garage door
            GPIO.setup(26, GPIO.OUT, initial=GPIO.HIGH)

            # Start garage door trigger listening thread
            self.logger.info("Listening for commands")
            doorTriggerThread = threading.Thread(target=doorTriggerLoop)
            doorTriggerThread.setDaemon(True)
            doorTriggerThread.start()

            self.logger.info("Configuring global settings")

            # Setting default home/away setting
            cfg.HOMEAWAY = 'home'

            # Last state of each garage door
            door_state = ''

            # time.time() of the last time the garage door changed state
            time_of_last_state_change = ''

            # Index of the next alert to send for each garage door
            alert_state = ''

            # Create alert sending objects
            alert_senders = {
                "Email": Email(),
                "IFTTT": IFTTT()
            }

            # Read initial states
            name = cfg.NAME
            state = get_garage_door_state(cfg.PIN)

            door_state = state
            time_of_last_state_change = time.time()
            alert_state = 0

            self.logger.info("Initial state of \"%s\" is %s", name, state)

            while True:
                name = cfg.NAME
                state = get_garage_door_state(cfg.PIN)
                time_in_state = time.time() - time_of_last_state_change

                # Check if the door has changed state
                if door_state != state:
                    door_state = state
                    time_of_last_state_change = time.time()
                    self.logger.info("State of \"%s\" changed to %s after %.0f sec", name, state, time_in_state)

                    # Reset alert when door changes state
                    alert_state = 0

                    # Reset time_in_state
                    time_in_state = 0

                # See if there are any alerts
                for alert in cfg.ALERTS:

                    if alert_state == 0:
                        # Get start and end times and only alert if current time is in between
                        time_of_day = int(datetime.now().strftime("%H"))
                        start_time = alert['start']
                        end_time = alert['end']
                        send_alert = False

                        # If system is set to away and the door is a open send an alert
                        if cfg.HOMEAWAY == 'away' and state == 'open':
                            send_alert = True
                        # Is start and end hours in the same day?
                        elif start_time < end_time:
                            # Is the current time within the start and end times and has the time elapsed and is this the state to trigger the alert?
                            if time_of_day >= start_time and time_of_day <= end_time and time_in_state > alert['time'] and state == alert['state']:
                                send_alert = True
                        elif start_time > end_time:
                            if time_of_day >= start_time or time_of_day <= end_time and time_in_state > alert['time'] and state == alert['state']:
                                send_alert = True

                        if send_alert:
                            send_alerts(self.logger, alert_senders, alert['recipients'], name, "%s has been %s for %d seconds!" % (name, state, time_in_state), state, time_in_state)
                            alert_state += 1

                # Poll every 1 second
                time.sleep(1)
        except KeyboardInterrupt:
            logging.critical("Terminating due to keyboard interrupt")
        except:
            logging.critical("Terminating due to unexpected error: %s", sys.exc_info()[0])
            logging.critical("%s", traceback.format_exc())

        GPIO.cleanup()

if __name__ == "__main__":
    PiGarageAlert().main()

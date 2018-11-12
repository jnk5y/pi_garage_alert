#!/usr/bin/env python
""" Pi Garage Manager

Authors: John Kyrus adapted from Richard L. Lynch <rich@richlynch.com>

Description: Use the accompying cordova app along with my node-rest-invoker https://github.com/jnk5y/node-rest-invoker
    to communicate with this garage door app. See state of garage door and open and close it from the app. Receive 
    notifications on your phone through the app and googles notification service using firebase.

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
import re
import sys
import signal
import json
import logging
import traceback
import socket
import time
from time import strftime
from datetime import datetime
from datetime import timedelta
from Queue import Queue
from multiprocessing.connection import Listener
import multiprocessing
import subprocess
import threading
import requests
import httplib2
import pigpio

sys.path.append('/usr/local/etc')
import pi_garage_manager_config as cfg

##############################################################################
# FIREBASE support https://firebase.google.com/docs/cloud-messaging/
##############################################################################

def send_notification(logger, name, state, time_in_state, alert_type, firebase_id):

    """ 
        Send a Firebase event using the FCM.
        Get the server key by following the URL at https://console.firebase.google.com/
    """
    logger.info("Sending Firebase event: value1 = \"%s\", value2 = \"%s\", value3 = \"%s\"", name, state, time_in_state )

    if firebase_id == '':
        logger.error("Firebase id is empty")
    elif cfg.FIREBASE_KEY == '':
        logger.error("Firebase key is empty in config file")
    else:
        time = format_duration(int(time_in_state))
        body = "Your garage door has been " + state + " for " + time
        headers = { "Content-type": "application/json", "Authorization": cfg.FIREBASE_KEY }
        payload = ''

        if alert_type == 'alert':
            payload = { "notification": { "title": "Garage door alert", "body": body, "sound": "default" }, "data": { "event": state }, "to": firebase_id }
        else:
            payload = { "data": { "event": state }, "to": firebase_id }
		
        try:
            requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, json=payload)
        except:
            logger.error("Exception sending Firebase event: %s", sys.exc_info()[0])

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

def get_garage_door_state():
    """Returns the state of the garage door

    if pi.read(22):
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
# Listener thread for getting/setting state and openning/closing the garage
##############################################################################

def message_listener():
    host = socket.gethostname()
    address = (host, int(cfg.NETWORK_PORT))
    listener = Listener(address)

    while True:
        # Receive incomming communications
        conn = listener.accept()
        received_raw = ''
        received_raw = conn.recv_bytes()
        listeningQueue.put(received_raw)
        listeningQueue.join()
        response = responseQueue.get()
        conn.send_bytes(response)
        responseQueue.task_done()
        time.sleep(1)

    conn.close()
    listener.close()

##############################################################################
# Main functionality
##############################################################################
# Queues for comminicating between threads
listeningQueue = Queue()
responseQueue = Queue()

# Set up logging
logger = logging.getLogger('pi_garage_manager')
log_fmt = '%(asctime)-15s %(levelname)-8s %(message)s'
log_level = logging.INFO

if sys.stdout.isatty():
    # Connected to a real terminal - log to stdout
    logging.basicConfig(format=log_fmt, level=log_level)
else:
    # Background mode - log to file
    logging.basicConfig(format=log_fmt, level=log_level, filename=cfg.LOG_FILENAME)

try:
    # Banner
    logger.info("==========================================================")
    logger.info("Pi Garage Manager Starting")

    # Initialize pigpio
    pi = pigpio.pi()
    logger.info("Configuring pin 15(GPIO 22) and 26(GPIO 7) for %s", cfg.NAME)
    # Configure the sensor pin as input
    pi.set_mode(22, pigpio.INPUT)
    pi.set_pull_up_down(23, pigpio.PUD_UP)
    # Configure the control pin for the relay to open and close the garage door
    pi.set_mode(7, pigpio.OUTPUT)

    # Configure global settings
    door_state = ''
    time_of_last_state_change = ''
    firebase_id = ''

    # Read initial states
    name = cfg.NAME
    home_away = 'home'
    state = get_garage_door_state()
    door_state = state
    time_of_last_state_change = time.time()
    alert_state = False

    logger.info("Initial state of \"%s\" is %s", name, state)

    # Start garage door trigger listening thread
    logger.info("Listening for commands")
    messageListenerThread = threading.Thread(target=message_listener)
    messageListenerThread.setDaemon(True)
    messageListenerThread.start()

    while True:
        state = get_garage_door_state()
        time_in_state = time.time() - time_of_last_state_change

        # Check if the door has changed state
        if door_state != state:
            door_state = state
            time_of_last_state_change = time.time()

            send_notification(logger, name, state, time_in_state, 'data', firebase_id)
            logger.info("State of %s changed to %s after %.0f sec", name, state, time_in_state)

            # Reset time_in_state and alert_state
            time_in_state = 0
            alert_state = False

        # See if there are any alerts
        for alert in cfg.ALERTS:
            if not alert_state:
                # Get start and end times and only alert if current time is in between
                time_of_day = int(datetime.now().strftime("%H"))
                start_time = alert['start']
                end_time = alert['end']
                send_alert = False

                # Is start and end hours in the same day?
                if start_time < end_time:
                    # Is the current time within the start and end times and has the time elapsed and is this the state to trigger the alert?
                    if time_of_day >= start_time and time_of_day <= end_time and time_in_state > alert['time'] and state == alert['state']:
                        send_alert = True
                else:
                    if (time_of_day >= start_time or time_of_day <= end_time) and time_in_state > alert['time'] and state == alert['state']:
                        send_alert = True

                if send_alert:
                    send_notification(logger, name, state, time_in_state, 'alert', firebase_id)
                    alert_state = True

        # If system is set to away and the door is a open send an alert
        if home_away == 'away' and state == 'open' and not alert_state:
            send_notification(logger, name, state, time_in_state, 'alert', firebase_id)
            alert_state = True

        # Deal with received messages
        if not listeningQueue.empty():
            received_raw = listeningQueue.get()
            received = received_raw.lower()
            response = 'unknown command'
            trigger = False

            if received == 'trigger':
                trigger = True
                if state == 'open':
                    response = 'closing'
                else:
                    response = 'opening'
            elif received == 'open' or received == 'up':
                if state == 'open':
                    response = 'already open'
                else:
                    response = 'opening'
                    trigger = True
            elif received == 'close' or received == 'down':
                if state == 'open':
                    response = 'closing'
                    trigger = True
                else:
                    response = 'already closed'
            elif received == 'home' or received == 'set to home':
                home_away = 'home'
                response = 'set to home'
            elif received == 'away' or received == 'set to away':
                home_away = 'away'
                response = 'set to away'
            elif received == 'state' or received == 'status':
                response = state + ' and ' + home_away
            elif received.startswith('firebase:'):
                firebase_id = received_raw.replace('firebase:','')
                response = 'ok'

            listeningQueue.task_done()
            responseQueue.put(response)
            responseQueue.join()
            logger.info('Received %s. Responded with %s', received_raw, response )

            if trigger:
		pi.write(7,0)
                time.sleep(2)
                pi.write(7,1)

            trigger = False

        time.sleep(1)

except:
    logging.critical("Terminating process")
finally:
    pi.stop()
    logger.error("Exiting pi_garage_manager.py")
    logger.error(sys.exc_info())
    sys.exit(0)

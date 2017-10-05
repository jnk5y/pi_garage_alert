#!/usr/bin/env python

##############################################################################
# Global settings
##############################################################################

# Describes the garage door being monitored
# time is in seconds
# start and end hours can be [0-23] - will alert only within those hours
NAME = "Garage Door"
ALERTS = [
    {
        'state': 'open',
        'time': 300,
        'start': 23,
        'end': 7,
    },
    {
        'state': 'open',
        'time': 7200,
        'start': 0,
        'end': 23,
    }
]

# All messages will be logged to stdout and this file
LOG_FILENAME = "/var/log/pi_garage_manager.log"

##############################################################################
# Home and away setting. Set it to away with the app when you are on vacation
# to trigger an alert immediately if the garage door is open.
# Default setting on startup is home
##############################################################################
HOMEAWAY = ''

##############################################################################
# Store Firebase notification information for mobile app notifications
# Insert your firebase key here. ID will be sent by the mobile app
##############################################################################
FIREBASE_KEY = 'key='
FIREBASE_ID = ''

##############################################################################
# IP address that pi garage manager is running on
##############################################################################
NETWORK_IP = '192.168.86.9'
NETWORK_PORT = '6000'

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
        'end': 7
    },
    {
        'state': 'open',
        'time': 7200,
        'start': 0,
        'end': 23
    }
]

# All messages will be logged to stdout and this file
LOG_FILENAME = "/var/log/pi_garage_manager.log"

##############################################################################
# Store Firebase notification information for mobile app notifications
# Insert your firebase key here.
##############################################################################
FIREBASE_KEY = 'key='

##############################################################################
# IP address that pi garage manager is running on
##############################################################################
NETWORK_IP = '192.168.86.9'
NETWORK_PORT = '6000'

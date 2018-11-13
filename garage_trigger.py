#!/usr/bin/env python
import sys
import os
import pigpio

if len(sys.argv) < 2:
    print "You must pass a parameter. (open, close, trigger, away, home, state)"

else:
    piAddress = '192.168.86.9'
    
    # Initialize pigpio
    pi = pigpio.pi(piAddress)

    # Configure the sensor pin as input
    pi.set_mode(22, pigpio.INPUT)
    pi.set_pull_up_down(23, pigpio.PUD_UP)
    
    # Configure the control pin for the relay to open and close the garage door
    pi.set_mode(7, pigpio.OUTPUT)

    state = ''
    if pi.read(22):
        state = 'open'
    else:
        state = 'closed'

    received_raw = sys.argv[1]
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

    print response

    if trigger:
        pi.write(7,0)
        time.sleep(2)
        pi.write(7,1)

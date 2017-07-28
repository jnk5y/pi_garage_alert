#!/usr/bin/env python
import sys
import os
from multiprocessing.connection import Client

if len(sys.argv) < 2:
    print "You must pass a parameter. (open, close, trigger, away, home, state)"

else:
#    host = os.getenv('GARAGE_ALERT_HOST', 'localhost')
#    port = os.getenv('GARAGE_ALERT_PORT', 6000)
#    address = (host, int(port))
    address = ('garage-container', 6000)
    conn = Client(address, authkey='secret password')
    conn.send_bytes(sys.argv[1])
    print conn.recv_bytes()
    conn.close()

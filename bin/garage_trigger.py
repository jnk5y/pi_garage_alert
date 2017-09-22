#!/usr/bin/env python
import sys
import os
import socket
from multiprocessing.connection import Client

if len(sys.argv) < 2:
    print "You must pass a parameter. (open, close, trigger, away, home, state)"

else:
    address = ('192.168.86.9', 6000)
    conn = Client(address)
    conn.send_bytes(sys.argv[1])
    print conn.recv_bytes()
    conn.close()


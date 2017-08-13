#!/usr/bin/env python
import sys
import os
from socket

if len(sys.argv) < 2:
    print "You must pass a parameter. (open, close, trigger, away, home, state)"

else:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.86.9", 6000))
    sock.sendall(sys.argv[1])
    result = sock.recv(1024)
    print result
    sock.close()

#!/usr/bin/env python
import sys
import os
import socket
from multiprocessing.connection import Client

if len(sys.argv) < 2:
    print "You must pass a parameter. (open, close, trigger, away, home, state)"

else:
    address = ('192.168.86.9', 6000)
    conn = Client(address, authkey='secret password')
    conn.send_bytes(sys.argv[1])
    print conn.recv_bytes()
    conn.close()

    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.connect(("192.168.86.9", 6000))
    #sock.sendall(sys.argv[1])
    #result = sock.recv(1024)
    #print result
    #sock.close()


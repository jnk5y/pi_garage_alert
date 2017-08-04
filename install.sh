#!/bin/bash
if [[ $# -eq 0 ]] ; then
    echo 'please pass your username'
    exit 0
fi

cp bin/pi_garage_manager.py /usr/local/sbin/
cp /usr/local/etc/pi_arage_manager_config.py /usr/local/etc/pi_arage_manager_config.old
cp etc/pi_garage_manager_config.py /usr/local/etc/
cp init.d/pi_garage_manager /etc/init.d/
chown $1 /usr/local/etc/pi_garage_manager_config.py

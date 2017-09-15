#!/bin/bash
if [[ $# -eq 0 ]] ; then
    echo 'please pass your username'
    exit 0
fi

cp bin/pi_garage_manager.py /usr/local/sbin/
cp etc/pi_garage_manager_config.py /usr/local/etc/
cp init.d/pi_garage_manager /etc/init.d/
update-rc.d pi_garage_manager defaults
chown $1 /usr/local/etc/pi_garage_manager_config.py

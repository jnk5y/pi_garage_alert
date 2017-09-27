#!/bin/bash

cp pi_garage_manager.py /usr/local/sbin/
cp pi_garage_manager_config.py /usr/local/etc/
cp pi_garage_manager /etc/init.d/
update-rc.d pi_garage_manager defaults

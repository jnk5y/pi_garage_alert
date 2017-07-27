FROM resin/rpi-raspbian:jessie

RUN cp etc/pi_garage_alert_config.py /usr/local/etc/ && \
    cp bin/pi_garage_alert.py /usr/local/sbin/ && \
    chmod u+x /usr/local/sbin/pi_garage_alert.py /usr/local/etc/pi_garage_alert_config.py

EXPOSE 6000

CMD [ "python", "/usr/local/sbin/pi_garage_alert.py"]

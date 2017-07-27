FROM resin/rpi-raspbian

COPY etc/pi_garage_alert_config.py /usr/local/etc/
COPY bin/pi_garage_alert.py /usr/local/sbin/
COPY bin/pi_garage_trigger.py /usr/local/sbin/

RUN chmod +x /usr/local/sbin/pi_garage_alert.py && \
    chmod +x /usr/local/etc/pi_garage_alert_config.py

RUN apt-get update && \
    apt-get install python \
     python-setuptools \
     python-dev \
     gcc \
     libffi-dev \
     python-pip && \
    pip install RPi.GPIO

EXPOSE 6000

CMD [ "python", "/usr/local/sbin/pi_garage_alert.py"]

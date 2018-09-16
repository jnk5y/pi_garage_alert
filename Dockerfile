FROM resin/rpi-raspbian

COPY pi_garage_manager_config.py /usr/local/etc/
COPY pi_garage_manager.py /usr/local/sbin/

RUN chmod +x /usr/local/sbin/pi_garage_manager.py && \
    chmod +x /usr/local/etc/pi_garage_manager_config.py

RUN apt-get update && \
    apt-get install python \
      python-setuptools \
      python-dev \
      libffi-dev \
      gcc && \
    easy_install pip && \
      pip install requests && \
      pip install httplib2 && \
      pip install RPi.GPIO 
      
EXPOSE 6000

CMD [ "python", "/usr/local/sbin/pi_garage_manager.py"]

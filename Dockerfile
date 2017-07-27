FROM resin/rpi-raspbian:jessie

RUN mkdir repo && \
    cd repo && \
    git clone --single-branch --depth 1 https://github.com/jnk5y/pi_garage_alert.git && \
    cd pi_garage_alert && \
    cp etc/pi_garage_alert_config.py /usr/local/etc/ && \
    cp bin/pi_garage_alert.py /usr/local/sbin/ && \
    chmod u+x /usr/local/sbin/pi_garage_alert.py /usr/local/etc/pi_garage_alert_config.py && \
    cd .. && \
    rm -Rf repo/

EXPOSE 6000

CMD [ "python", "/usr/local/sbin/pi_garage_alert.py"]

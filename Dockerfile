FROM    centos:latest

RUN     mkdir /opt/railnation && \
        /usr/bin/curl 'https://bootstrap.pypa.io/get-pip.py' | /usr/bin/python && \
        pip install cherrypy requests jsonschema

ENV     PYTHONPATH /opt/railnation/lib

EXPOSE  8080

CMD     /usr/bin/python -m railnation

ADD     . /opt/railnation


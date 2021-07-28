FROM python:3.8-slim

COPY ../../docker-server-4.py /tmp/server.py

ENTRYPOINT ["/usr/local/bin/python3", "/tmp/server.py", "EdgeServer-1", "-1"]
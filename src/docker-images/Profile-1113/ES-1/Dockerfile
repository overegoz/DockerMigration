FROM python:3.8

ENV PYTHONUNBUFFERED=1

COPY docker-server-4.py /tmp/server.py
COPY common.py /tmp/common.py
COPY Profile.py /tmp/Profile.py

ENTRYPOINT ["/usr/local/bin/python3", "/tmp/server.py", "EdgeServer-1", "1113"]

#!/bin/bash

docker run -p 20005:20005/udp -d --name profile0 twoon/profile0:es1  # for ES1
docker run -p 20006:20006/udp -d --name profile0 twoon/profile0:es2  # for ES2

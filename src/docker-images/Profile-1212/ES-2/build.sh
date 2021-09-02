#!/bin/bash

cp ../../../docker-server-4.py .
cp ../../../common.py .
cp ../../../Profile.py .

docker build -t twoon/profile1212:es2 .

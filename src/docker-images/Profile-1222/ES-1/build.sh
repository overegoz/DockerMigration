#!/bin/bash

cp ../../../docker-server-4.py .
cp ../../../common.py .
cp ../../../Profile.py .

docker build -t twoon/profile1222:es1 .

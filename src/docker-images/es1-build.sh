#!/bin/bash

docker stop $(docker ps -a -q)
docker container prune -f

cd Profile-0/ES-1
sh build.sh
cd ../../

cd Profile-1/ES-1
sh build.sh
cd ../../

#!/bin/bash

docker stop $(docker ps -a -q)
docker container prune -f

cd docker-images/Profile-0/ES-1
sh build.sh
cd ../../../

cd docker-images/Profile-1/ES-1
sh build.sh
cd ../../../

docker image prune -f
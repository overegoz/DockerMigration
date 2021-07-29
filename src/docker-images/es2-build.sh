#!/bin/bash

docker container prune -f
cd Profile-0/ES-2
sh build.sh
cd ../../

cd Profile-1/ES-2
sh build.sh
cd ../../


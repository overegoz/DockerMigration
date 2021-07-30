#!/bin/bash

docker stop $(docker ps -a -q)
docker container prune -f

cd docker-images/Profile-0/ES-2
sh build.sh
cd ../../../

cd docker-images/Profile-1/ES-2
sh build.sh
cd ../../../

# FC를 할거니까, Profile-2에서는 ES2의 img 만들지 말기
# cd docker-images/Profile-2/ES-2
# sh build.sh
# cd ../../../

docker image prune -f
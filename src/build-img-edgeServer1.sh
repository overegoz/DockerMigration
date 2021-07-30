#!/bin/bash

docker stop $(docker ps -a -q)
docker container prune -f

cd docker-images/Profile-0/ES-1
sh build.sh
cd ../../../

cd docker-images/Profile-1/ES-1
sh build.sh
cd ../../../

cd docker-images/Profile-2/ES-1
sh build.sh
cd ../../../

# migr 과정에서 만든 이미지 삭제하기
docker rmi twoon/profile2:es2

docker image prune -f
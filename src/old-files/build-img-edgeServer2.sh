#!/bin/bash
# -----------------------------
# Edge Server 2에서 생성할 도커 이미지를 생성하는 부분
# -----------------------------
docker stop $(docker ps -a -q)
docker container prune -f
# -----------------------------
cd docker-images/Profile-0/ES-2
sh build.sh
cd ../../../
# -----------------------------
cd docker-images/Profile-1/ES-2
sh build.sh
cd ../../../
# -----------------------------
# FC를 할거니까, Profile-2에서는 ES2의 img 만들지 말기
# cd docker-images/Profile-2/ES-2
# sh build.sh
# cd ../../../
# 대신, migr 으로 생성된게 있으면 지우자
docker rmi twoon/profile2:es2
# -----------------------------
cd docker-images/Profile-3/ES-2
sh build.sh
cd ../../../
# -----------------------------
cd docker-images/Profile-4/ES-2
sh build.sh
cd ../../../
# -----------------------------
cd docker-images/Profile-111/ES-2
sh build.sh
cd ../../../
# -----------------------------
cd docker-images/Profile-112/ES-2
sh build.sh
cd ../../../
# -----------------------------
docker image prune -f
# -----------------------------
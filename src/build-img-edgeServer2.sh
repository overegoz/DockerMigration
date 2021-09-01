#!/bin/bash
# -----------------------------
# Edge Server 2에서 생성할 도커 이미지를 생성하는 부분
# -----------------------------
docker stop $(docker ps -a -q)
docker container prune -f
# -----------------------------
# FC를 할거니까, Profile-1111에서는 ES2의 img 만들지 말기
# cd docker-images/Profile-1111/ES-2
# sh build.sh
# cd ../../../
# 대신, migr 으로 전달 받은게 있으면 지우자
docker rmi twoon/profile2:es2
# -----------------------------
# 1112 : DC
cd docker-images/Profile-1112/ES-2
sh build.sh
cd ../../../
# -----------------------------
docker image prune -f
# -----------------------------
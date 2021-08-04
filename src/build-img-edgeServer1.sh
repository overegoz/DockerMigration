#!/bin/bash
# -----------------------------
# Edge Server 1에서 생성할 도커 이미지를 생성하는 부분
# -----------------------------
# 현재 구동중인 컨테이너 모두 정지하기
docker stop $(docker ps -a -q)
docker container prune -f
# -----------------------------
cd docker-images/Profile-0/ES-1
sh build.sh
cd ../../../
# -----------------------------
cd docker-images/Profile-1/ES-1
sh build.sh
cd ../../../
# -----------------------------
cd docker-images/Profile-2/ES-1
sh build.sh
cd ../../../
# FC migr 과정에서 만든 이미지 삭제하기
docker rmi twoon/profile2:es2
# -----------------------------
cd docker-images/Profile-3/ES-1
sh build.sh
cd ../../../
# -----------------------------
cd docker-images/Profile-4/ES-1
sh build.sh
cd ../../../
# -----------------------------
docker image prune -f
# -----------------------------
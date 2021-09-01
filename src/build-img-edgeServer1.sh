#!/bin/bash
# -----------------------------
# Edge Server 1에서 생성할 도커 이미지를 생성하는 부분
# -----------------------------
# 현재 구동중인 컨테이너 모두 정지하고 삭제하기
docker stop $(docker ps -a -q)
docker container prune -f
# -----------------------------
# 1111 : FC
cd docker-images/Profile-1111/ES-1
sh build.sh
cd ../../../
# FC migr 과정에서 만든 이미지 삭제하기
docker rmi twoon/profile1111:es2
# -----------------------------
# 이름없는 이미지 삭제하기
docker image prune -f
# -----------------------------
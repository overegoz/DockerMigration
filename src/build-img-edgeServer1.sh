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
# 1112 : DC
cd docker-images/Profile-1112/ES-1
sh build.sh
cd ../../../
# -----------------------------
# 1113 : LR
cd docker-images/Profile-1113/ES-1
sh build.sh
cd ../../../
# -----------------------------
# 1121 : FC
cd docker-images/Profile-1121/ES-1
sh build.sh
cd ../../../
# FC migr 과정에서 만든 이미지 삭제하기
docker rmi twoon/profile1121:es2
# -----------------------------
# 1122 : DC
cd docker-images/Profile-1122/ES-1
sh build.sh
cd ../../../
# -----------------------------
# 1123 : LR
cd docker-images/Profile-1123/ES-1
sh build.sh
cd ../../../
# -----------------------------
# 1212 : DC
cd docker-images/Profile-1212/ES-1
sh build.sh
cd ../../../
# -----------------------------
# 1213 : LR
cd docker-images/Profile-1213/ES-1
sh build.sh
cd ../../../
# -----------------------------
# 이름없는 이미지 삭제하기
docker image prune -f
# -----------------------------
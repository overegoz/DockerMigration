#!/bin/bash
# -----------------------------
# Edge Server 2에서 생성할 도커 이미지를 생성하는 부분
# -----------------------------
docker stop $(docker ps -a -q)
docker container prune -f
# -----------------------------
# 1111은 FC를 할거니까, ES2의 img 만들지 말기
# cd docker-images/Profile-1111/ES-2
# sh build.sh
# cd ../../../
# 대신, migr 으로 전달 받은게 있으면 지우자
docker rmi twoon/profile1111:es2
# -----------------------------
# 1112 : DC
cd docker-images/Profile-1112/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 1113 : LR
cd docker-images/Profile-1113/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 1121은 FC를 할거니까, ES2의 img 만들지 말기
# cd docker-images/Profile-1121/ES-2
# sh build.sh
# cd ../../../
# 대신, migr 으로 전달 받은게 있으면 지우자
docker rmi twoon/profile1121:es2
# -----------------------------
# 1122 : DC
cd docker-images/Profile-1122/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 1123 : LR
cd docker-images/Profile-1123/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 1222 : DC
cd docker-images/Profile-1222/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 1223 : LR
cd docker-images/Profile-1223/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 2112 : DC
cd docker-images/Profile-2112/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 2113 : LR
cd docker-images/Profile-2113/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 2122 : DC
cd docker-images/Profile-2122/ES-2
sh build.sh
cd ../../../
# -----------------------------
# 2123 : LR
cd docker-images/Profile-2123/ES-2
sh build.sh
cd ../../../
# -----------------------------
docker image prune -f
# -----------------------------
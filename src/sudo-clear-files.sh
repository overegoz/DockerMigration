#!/bin/bash

rm -rf /home/daniel/migration/DiffCopyFiles/*
rm -rf /home/daniel/migration/DC-CheckPoints/*

rm -rf /home/daniel/migration/FullCopyImages/*
rm -rf /home/daniel/migration/FC-CheckPoints/*

rm -rf /home/daniel/migration/LogReplayRecords/*
# log-replay는 체크포인트 생성 안함: 체크포인트 저장을 위한 디렉토리가 없음

rm diff-*.txt
rm log-*.txt
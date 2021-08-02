#!/bin/bash

# ------------------------------------------------------------------
# Full-Copy (FC) : 파일 지우지 말자... 나중에 필요할 듯
#rm -rf /home/daniel/migration/FullCopyImages/*
#rm -rf /home/daniel/migration/FC-CheckPoints/*
# ------------------------------------------------------------------
# Diff-Copy (DC) : 파일 지우지 말자... 나중에 필요할 듯
#rm -rf /home/daniel/migration/DiffCopyFiles/*
#rm -rf /home/daniel/migration/DC-CheckPoints/*
# ------------------------------------------------------------------
# Log-Replay (LR) : 파일 지우지 말자... 나중에 필요할 듯
#rm -rf /home/daniel/migration/LogReplayRecords/*
# log-replay는 체크포인트 생성 안함: 체크포인트 저장을 위한 디렉토리가 없음
# ------------------------------------------------------------------
# 그 외...
rm diff-*.txt
rm log-*.txt
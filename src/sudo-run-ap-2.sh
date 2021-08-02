#!/bin/bash

# 스크립트 실행 시, 어떤 프로파일을 실행할 지에 대한 숫자 번호 필요
export PYTHONUNBUFFERED=1  # 파이썬이 stdout 출력을 버퍼링 하는 걸 막음
python3 ap-3.py AP-2 $1
#-*- encoding: utf8 -*-
import socket 
import time
import signal, os
import datetime

import common


my_name = common.logger_name

# listen 소켓 생성
local_ip = common.ip[my_name]
local_port = common.port[my_name]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

# 로그 파일 만들기
f = open(common.get_now() + ".log", 'w')

# 로거 실행에 대한 로그 기록하기
log = my_name + common.delim + common.get_now() + common.start_msg
f.write(log)

def handler(signum, frame):  # CTRL+C 시그널 핸들러 만들기
    print(common.sigint_msg)
    sock.close()
    f.close()
    exit()

signal.signal(signal.SIGINT, handler)  # 시그널 핸들러 등록

while(True):
    # 메시지 수신
    time.sleep(common.LOGGER_SLEEP)
    recv_msg = common.udp_recv(sock, common.bufsiz)

    # 메시지 기록
    time.sleep(common.LOGGER_SLEEP)
    if len(recv_msg) > 0:
        f.write(recv_msg)

    else:
        pass

    # 특정 이벤트가 발생한 경우에는 controller에게 이 사실을 알려줘야 함

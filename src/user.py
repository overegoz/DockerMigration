#-*- encoding: utf8 -*-
import socket 
import time
import signal, os
import datetime
import common


my_name = common.user_name

# listen 소켓 생성
local_ip = common.ip[my_name]
local_port = common.port[my_name]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

def handler(signum, frame):  # CTRL+C 시그널 핸들러 만들기
	print(common.sigint_msg)
    # 코드마다 마무리 작업이 달라서, common 파일로 옮기지 못함
	sock.close()  
	exit()

signal.signal(signal.SIGINT, handler)  # 시그널 핸들러 등록

common.send_log(my_name, common.start_msg)

# 처음에는 무조건 AP-1에 연결한다고 가정한다
association = common.ap1_name
common.udp_send(sock, association, "HELO")

while(True):
    # AP 에게 서비스 요청 메시지 보내기
    time.sleep(common.USER_REQ_INTERVAL/2.0)
    #send_msg = my_name + common.delim + "test"
    #common.udp_send(sock, association, send_msg)

    # AP로 부터 메시지 수신하기
    time.sleep(common.USER_REQ_INTERVAL/2.0)
    recv_msg = common.udp_recv(sock, common.bufsiz)
    #if( len(recv_msg) > 0 ) :
    #    pass
    #else:
    #    pass
#-*- encoding: utf8 -*-
import socket 
import time
import signal, os
import datetime
import common


my_name = common.controller_name

# listen 소켓 생성
local_ip, local_port = common.ip[my_name], common.port[my_name]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

def handler(signum, frame):  # CTRL+C 시그널 핸들러 만들기
	print(common.sigint_msg)
    # 코드마다 마무리 작업이 달라서, common 파일로 옮기지 못함
	sock.close()  
	exit()

signal.signal(signal.SIGINT, handler)  # 시그널 핸들러 등록

common.send_log(sock, my_name, common.start_msg)

# 현재, USER가 연결되어있는 AP
# 처음에는 모른다고 하고, logger가 HELO 메시지를 전해주면 setting
user_curr_ap = ""

while(True):
    """
    컨트롤러는 
    1. Logger로 부터 주요 이벤트 수신(HELO, BYEE)
    2. Migration 발생하면 old AP로 부터 관련 데이터 수신하고,
       어떤 방식의 migr을 할지를 old AP와 new AP에게 알려주기
    """
    # 메시지 수신
    time.sleep(common.SHORT_SLEEP)
    recv_msg, addr = common.udp_recv(sock, common.bufsiz)

    if len(recv_msg) > 0:  # 수신한 메시지가 있다면...
        sender_ip = addr[0]

        # LOGGER로 부터 받은 메시지라면... HELO/BYEE 이벤트에 대한 것이지
        if sender_ip == common.ip[common.logger_name]:
            words = recv_msg.decode().split(common.delim)
            if words[2] == common.USER_HELLO:
                    pass

        # AP로 부터 받은 것이라면, migr 기법 결정에 필요한 정보를 받은것이겠지
        elif sender_ip == common.ip[common.ap1_name] \
             or sender_ip == common.ip[common.ap2_name]:
            pass

        else:
            assert False

    else: # 수신한 메시지가 없으면, 그냥 패스!
        pass
#-*- encoding: utf8 -*-
import socket 
import time
import signal, os
import datetime
import common


my_name = common.user_name

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

common.send_log(sock, my_name, my_name, common.start_msg)

# 처음에는 무조건 AP-1에 연결한다고 가정한다
curr_ap = common.ap1_name
common.udp_send(sock, curr_ap, common.USER_HELLO)

def get_ap(curr_ap):
    # 어떤 AP와 연결할지에 대한 결정을 하는 함수
    ap_old = curr_ap
    ap_new = curr_ap  # 일단은 바뀌지 않는 것으로 코딩...
    return ap_new, ap_old

counter = 0
while(True):
    """
    USER는 두 가지 통신만 한다.
    1. 현재 연결된 AP와 REQ/RES 송수신
    2. 이벤트에 대해서 Logger에 전송
    """
    # 어떤 AP에 연결할지를 확인
    curr_ap, old_ap = get_ap(curr_ap)

    if curr_ap == old_ap:  # AP가 변경되지 않음
        # 현재 연결된 AP 에게 서비스 요청 메시지 보내기
        # 마지막에 숫자 카운터 번호를 넣어서 tracking 할 수 있도록...
        time.sleep(common.USER_REQ_INTERVAL/2.0)
        send_msg = my_name + common.delim + common.SVC_REQ \
                   + common.delim + str(counter)
        common.udp_send(sock, curr_ap, send_msg)
        common.send_log(sock, my_name, curr_ap, send_msg + common.delim + "(sent)")
        counter += 1

        # 현재 연결된 AP로 부터 메시지 수신하기
        time.sleep(common.USER_REQ_INTERVAL/2.0)
        recv_msg, addr = common.udp_recv(sock, common.bufsiz)
        if( len(recv_msg) > 0 ) :  # 실제로 받은 메시지가 있다면 로깅
            # 현재 연결된 AP로 부터 데이터를 수신한 것이 맞는지 확인
            assert common.ip[curr_ap] == addr[0]

            # 수신 메시지를 로그에 기록하기
            common.send_log(sock, my_name, recv_msg + common.delim + "(recv)")
        else:
            pass
    else:  # 접속 AP가 변경됨
        # new AP로 HELO 먼저 보내고,
        time.sleep(common.USER_HANDOVER_DELAY/2.0)
        send_msg = my_name + common.delim + common.USER_HELLO \
                   + common.delim
        common.udp_send(sock, curr_ap, send_msg)
        common.send_log(sock, my_name, curr_ap, 
                        send_msg + common.delim + "(sent)")
        
        # 다음으로, old AP에 BYEE 보낸다.
        time.sleep(common.USER_HANDOVER_DELAY/2.0)
        send_msg = my_name + common.delim + common.USER_BYE \
                   + common.delim
        common.udp_send(sock, old_ap, send_msg)
        common.send_log(sock, my_name, old_ap, 
                        send_msg + common.delim + "(sent)")
        pass


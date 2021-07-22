#-*- encoding: utf8 -*-
import socket 
import time
import signal, os
import datetime
import common


my_name = common.logger_name

# listen 소켓 생성
local_ip,local_port = common.ip[my_name], common.port[my_name]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

# 로그 파일 만들기
f = open(common.get_now() + ".log", 'w')

common.logger_log(f=f, you=my_name, msg=common.start_msg) # 로거가 시작했다는 로그 남기기

def handler(signum, frame):  # CTRL+C 시그널 핸들러 만들기
    print(common.sigint_msg)
    sock.close()
    f.close()
    exit()

signal.signal(signal.SIGINT, handler)  # 시그널 핸들러 등록

while(True):
    """
    Logger는 기본적으로 메시지를 수신하기만 한다.
    하지만, HELO/BYEE 이벤트가 발생하면 컨트롤러에게 알려준다.
    """
    # 메시지 수신
    time.sleep(common.SHORT_SLEEP)
    recv_msg, _ = common.udp_recv(sock, common.bufsiz)

    # 메시지 기록
    time.sleep(common.SHORT_SLEEP)
    if len(recv_msg) > 0:  # 수신한 메시지가 있다면...
        # 수신한 메시지를 로그에 기록
        common.file_write(f,recv_msg)

        # USER가 HELO/BYEE 메시지를 보낸 경우, controller에게 이 사실을 알려줘야 함
        # AP가 보내온 로그 형식은... (user는 한명 밖에 존재하지 않음)
        # : <시간> <AP-X> <USER> <메시지: HELO 또는 BYEE>
        words = recv_msg.decode().split(common.delim)
        if words[1] == common.ap1_name or words[1] == common.ap2_name:  # AP로부터 도착한 메시지중...
            if words[3] == common.USER_HELLO or words[3] == common.USER_BYE: # HELO/BYEE인 경우...
                ap_name, event = words[1], words[3]
                msg = common.user_name + common.delim + event + common.delim + ap_name
                common.udp_send(sock, common.controller_name, msg)  # 컨트롤러에 알리기
                common.logger_log(f, common.controller_name, 
                                  msg + common.delim + "(sent to controller)")  # 로그로 기록하기
            else:
                pass 
    else: # 수신한 메시지가 없으면, 그냥 패스!
        pass


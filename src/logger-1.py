#-*- encoding: utf8 -*-
import socket 
import time
import signal, os
import datetime
import common


# -------------------------------------------------------------------
my_name = common.logger_name
# -------------------------------------------------------------------
# listen 소켓 생성
local_ip,local_port = common.ip[my_name], common.port[my_name]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기
# -------------------------------------------------------------------
# 로그 파일 만들기
f = open(common.get_now() + ".log", 'w')
# -------------------------------------------------------------------
def file_write(f, msg):
	# 파일에 기록할 때, 개행문자를 추가하자
	f.write(msg + "\n")
	print(msg + "\n")  # 테스트용

def logger_log(f, you, msg):
	log = common.str4(common.get_now(), my_name, you, msg)
	file_write(f, log)

# -------------------------------------------------------------------
logger_log(f=f, you=my_name, msg=common.start_msg) # 로거가 시작했다는 로그 남기기
# -------------------------------------------------------------------
def handler(signum, frame):  # CTRL+C 시그널 핸들러 만들기
	print(common.sigint_msg)
	sock.close()
	f.close()
	exit()

signal.signal(signal.SIGINT, handler)  # 시그널 핸들러 등록
# -------------------------------------------------------------------
while(True):
	"""
	Logger는 기본적으로 메시지를 수신하기만 한다.
	하지만, HELO/BYEE 이벤트가 발생하면 컨트롤러에게 알려준다.
	"""
	# 메시지 수신
	recv_msg, _ = common.udp_recv(sock, my_name, common.bufsiz, common.SHORT_SLEEP)

	# 메시지 기록
	if len(recv_msg) > 0:  # 수신한 메시지가 있다면...
		file_write(f,recv_msg)  # [LRx] 수신한 메시지를 로그에 기록

		# USER가 HELO/BYEE 메시지를 보낸 경우, controller에게 이 사실을 알려줘야 함
		# AP가 보내온 로그 형식은... (user는 한명 밖에 존재하지 않음)
		# : <시간> <AP-X> <USER> <메시지: HELO 또는 BYEE>
		words = recv_msg.split(common.delim)
		sender = words[1]
		event = words[3]
		if sender == common.ap1_name or sender == common.ap2_name:  # AP로부터 도착한 메시지...
			if event == common.USER_HELLO or event == common.USER_BYE: # [LR1][LR2] HELO/BYEE 면...
				ap_name = words[1]
				msg = common.str3(my_name, event, ap_name)
				common.udp_send(sock, my_name, common.controller_name, msg, 
								common.SHORT_SLEEP)  # [LS1][LS2] 컨트롤러에 알리기
				logger_log(f, common.controller_name, 
									common.str2(msg, "(sent to controller)"))  # 로그로 기록하기
			else:
				pass 
	else: # 수신한 메시지가 없으면, 그냥 패스!
		pass


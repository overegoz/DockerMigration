#-*- encoding: utf8 -*-
import socket 
import time
import signal, os, sys
import datetime
import common

"""
실행 방법
$ python3 user.py <USER 프로필>
따라서, command line arg 개수는 총 2개 (코드이름 + 1개 인자)
<USER 프로필> : 숫자번호
"""
# -------------------------------------------------------------------
# command line arg 처리
# -------------------------------------------------------------------
err_msg = ""
if len(sys.argv) != 2:
	# 인자 갯수가 정확하지 않음
	err_msg = "Need 1 arg(s): <profile>, but you entered " + str(sys.argv)
elif int(sys.argv[1]) not in common.profile_ids:
	# 정의되지 않은 프로필 번호가 주어짐	
	err_msg = "Incorrect profile id! " + str(sys.argv[1])
else:
	pass

if len(err_msg) > 0:
	# 오류가 있었다는 것임. 로그 전송 하지 않고, 터미널 출력하자
	assert False, "ERR MSG: " + err_msg
# -------------------------------------------------------------------
my_name = common.user_name
profile = int(sys.argv[1])
# -------------------------------------------------------------------
# listen 소켓 생성
local_ip, local_port = common.ip[my_name], common.port[my_name]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기
# -------------------------------------------------------------------
def handler(signum, frame):  # CTRL+C 시그널 핸들러 만들기
# 코드마다 마무리 작업이 달라서, common 파일로 옮기지 못함
	print(common.sigint_msg)
	# ap에게 알려주기
	common.udp_send(sock, my_name, curr_ap,
					common.str2(my_name, common.USER_EXIT), 
					common.SHORT_SLEEP)
	# 소켓 닫고 나가기	
	sock.close()  
	exit()

signal.signal(signal.SIGINT, handler)  # 시그널 핸들러 등록
# -------------------------------------------------------------------
# 실행 되었다는 것을 Logger에 알리기
common.send_log(sock, my_name, my_name, common.str2(common.start_msg,str(sys.argv)))
# -------------------------------------------------------------------
# 처음에는 무조건 AP-1에 연결한다고 가정한다
curr_ap = common.ap1_name
# user가 AP에 연결 되었음을 알리기 (HELLO)
common.udp_send(sock, my_name, curr_ap, \
				common.str2(my_name, common.USER_HELLO), common.SHORT_SLEEP)  
# -------------------------------------------------------------------
req_int = common.USER_REQ_INTERVAL
handover_counter = common.INTMAX  # 핸드오버가 언제 발생하지 제어
if profile > 0:
	# 프로파일 번호에 따라서 설정값을 불러옴
	req_int = common.prof.get_req_int(profile)
	handover_counter = common.prof.get_ho_cnt(profile)
elif profile == -1:  # 테스트용
	#handover_counter = 3
	handover_counter = -1
elif profile == 0:  # test
	handover_counter = 5
else:
	pass  # 테스트용
# -------------------------------------------------------------------
def check_ap(current_ap, handover):
	# 어떤 AP와 연결할지에 대한 결정을 하는 함수
	if handover == False:
		ap_old = current_ap
		ap_new = current_ap  # 일단은 바뀌지 않는 것으로 코딩...
	else:
		print('curr: ', current_ap)
		assert current_ap == common.ap1_name
		ap_old = current_ap
		ap_new = common.ap2_name

	return ap_new, ap_old
# -------------------------------------------------------------------
# 최초로 실행할때에는 edge server 가 준비될 때 까지 기다림
# AP에게 HELLO 메시지는 이미 보냈음
assert curr_ap == common.ap1_name
while(True):
	recv_msg, _ = common.udp_recv(sock, my_name, common.bufsiz, common.SHORT_SLEEP)
	if len(recv_msg) > 0:
		words = recv_msg.split(common.delim)
		sender = words[0]
		# 현재 연결된 AP로 부터 데이터를 수신한 것이 맞는지 확인
		# 수신 메시지를 로그로 남겨주기만 하면 됨
		assert sender == curr_ap
		if words[1] == common.ES_READY:
			break
	else:
		pass
# -------------------------------------------------------------------
# 본격적으로 REQ-RES 시작!
counter = 0  # req를 보낼건데, cnt 번호를 붙여서 tracking 가능하도록
while(True):
	"""
	USER는 두 가지 통신만 한다.
	1. 현재 연결된 AP와 REQ/RES 송수신
	2. 이벤트에 대해서 Logger에 전송
	"""
	# 어떤 AP에 연결할지를 확인
	curr_ap, old_ap = check_ap(curr_ap, counter == handover_counter)

	if curr_ap == old_ap:  # AP가 변경되지 않음
		# 현재 연결된 AP 에게 서비스 요청 메시지 보내기
		# 마지막에 숫자 카운터 번호를 넣어서 tracking 할 수 있도록...
		send_msg = common.str3(my_name, common.SVC_REQ, str(counter))
		common.udp_send(sock, my_name, curr_ap, send_msg, req_int/2.0)
		counter += 1

		# [UR1] 현재 연결된 AP로 부터 서비스 응답 메시지 수신하기
		recv_msg, addr = common.udp_recv(sock, my_name, common.bufsiz, req_int/2.0)
		if len(recv_msg) > 0:  
			print('recv msg: ', recv_msg)
			words = recv_msg.split(common.delim)

			"""
			- 현재 연결된 AP로 부터 데이터를 수신한 것이 맞는지 확인 => 주석처리
			- user의 NIC 큐에 버퍼링 된 수신 데이터가 있을경우, 오류가 발생하는 버그있음
			sender = words[0]
			assert sender == curr_ap, 'recv msg: {}'.format(recv_msg)
			"""

			cmd = words[1]
			if cmd == common.SVC_RES:
				# 서비스에 대한 응답이면 수신 메시지를 로그로 남겨주기만 하면 됨
				# udp_recv에서 로그 남기니까, 그냥 pass 하면 됨
				pass
			else: assert False
		else: pass
	else:  # 접속 AP가 변경됨
		print("핸드오버 발생 : {} => {}".format(old_ap, curr_ap))
		# [US2] new AP로 HELO 먼저 보내고,
		send_msg = common.str2(my_name, common.USER_HELLO)
		#print("send : ", send_msg)
		common.udp_send(sock, my_name, curr_ap, send_msg, common.USER_HANDOVER_DELAY/2.0)
		
		# [US3] 다음으로, old AP에 BYEE 보낸다.
		send_msg = common.str2(my_name, common.USER_BYE)
		#print("send : ", send_msg)
		common.udp_send(sock, my_name, old_ap, send_msg, common.USER_HANDOVER_DELAY/2.0)
		
		"""
		handover counter를 초기화
		: counter를 증가시키지 않고 while 루프를 다시 시작하게 되면
		  handover 직후, check_ap에서 오류남
		"""
		handover_counter = -1


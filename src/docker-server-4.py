"""
EdgeServer 즉 도커 컨테이너에서 실행할 코드이다.
"""
import socket 
import time
import signal, os, sys
import datetime
import common

"""
실행 방법
$ python3 docker-server.py <이름> <프로파일>
따라서, command line arg 개수는 총 4개 (코드이름 + 3개 인자)
<이름> : EdgeServer1 또는 EdgeServer2
<ES 프로파일> : 숫자번호
<migr 기법> : common에 정의된 MIGR_FC, MIGR_DC, MIGR_LR 중 하나
"""
# -------------------------------------------------------------------
# command line arg 처리
# -------------------------------------------------------------------
err_msg = ""
if len(sys.argv) != 3:
	# 인자 갯수가 정확하지 않음
	err_msg = "Need 3 args: <edge server name> <profile>, but you entered " + str(sys.argv)
elif sys.argv[1] != common.edge_server1_name \
	and sys.argv[1] != common.edge_server2_name:
	# EdgeServer 이름이 정확하지 않음
	err_msg = "Incorrect EdgeServer name! " + str(sys.argv[1])
elif int(sys.argv[2]) not in common.profile_ids:
	# 정의되지 않은 프로필 번호가 주어짐	
	err_msg = "Incorrect profile id! " + str(sys.argv[2])
else:  # 아무 문제가 없음
	pass

if len(err_msg) > 0:
	# 오류가 있었다는 것임
	# 도커는 터미널 출력을 보기 어려우니까, 오류 메시지를 로그로 전송
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	common.send_log(sock, "EdgeServer-X", "EdgeServer-X", err_msg)
	sock.close()
	exit()  # 즉시 종료

# -------------------------------------------------------------------
my_name = sys.argv[1]
my_ap_name = ""
if my_name == common.edge_server1_name:
	my_ap_name = common.ap1_name
elif my_name == common.edge_server2_name:
	my_ap_name = common.ap2_name
else:
	assert False

# -------------------------------------------------------------------
profile = int(sys.argv[2])
# -------------------------------------------------------------------
"""
- 컨테이너는 기본적으로 0.0.0.0 IP 주소를 가진다. 따라서 서버 IP 주소를
0.0.0.0 으로 설정해 줘야 한다.
- 포트 포워딩은 서버 수신 포트만 해 주면 된다.
"""
# listen 소켓 생성
if( profile == -1 ):  # 도커 없이 실행하는, 테스트용 run
	localIP = common.ip[my_name]
else:
	localIP = common.ip_fake[my_name]

print(localIP, ", ", localPort)
localPort = common.port[my_name]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind((localIP, localPort)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

def handler(signum, frame):
	print(common.sigint_msg)
	sock.close()
	exit()

signal.signal(signal.SIGINT, handler)

# 실행 되었다는 것을 Logger에 알리기
common.send_log(sock, my_name, my_name, 
				common.str2(common.start_msg, str(sys.argv)))

# 프로파일에 따라서 사전 작업을 수행함
profile = int(sys.argv[2])
common.run_profile(my_name, profile)

# 서비스를 할 준비가 되었음을 AP에게 알림
send_msg = common.str2(my_name, common.ES_READY)
common.udp_send(sock, my_name, my_ap_name, send_msg, common.SHORT_SLEEP)

# 서비스를 시작
while(True): 
	"""
	Edge서버는 두 가지 통신만 한다.
	1. AP를 통해서 받은 USER의 REQ 
		: AP는 USER가 보낸 메시지를 그대로 전달해 줌
		: USER SVCQ <숫자>
	2. USER의 REQ에 대한 응답을 AP로 보내는 것
		: EdgeServer<서버번호> SVCR <같은 숫자>
	"""
	# 직접 연결된 AP로 부터 데이터 수신하기
	try:
		recv_msg, _ = common.udp_recv(sock, my_name, common.bufsiz, common.SHORT_SLEEP) 
		if len(recv_msg) > 0:
			words = recv_msg.split(common.delim)

			# sender 정보가 맞는지 확인
			if words[0] != my_ap_name:
				common.send_log(sock, my_name, my_name, \
								common.str2("invalid-sender-name", recv_msg))
				assert False

			# [ER1][ER2] 서비스 요청 메시지가 맞는지 확인
			if words[1] != common.SVC_REQ:
				common.send_log(sock, my_name, my_name, \
								common.str2("invalid-command-received", recv_msg))
				assert False

			# 수신 메시지가 형식에 맞는지 확인하기
			if len(words) != 3:
				common.send_log(sock, my_name, my_name, 
								common.str2("wrong-msg-format", recv_msg))
				assert False

			# 직접 연결된 AP에게 전송할 메시지 준비하기
			counter = words[2]
			send_msg = common.str3(my_name, common.SVC_RES, counter)
			# [ES1][ES2] 직접 연결된 AP에게 메시지 전송
			common.udp_send(sock, my_name, my_ap_name, send_msg, common.SHORT_SLEEP)
	except socket.error:
		# AP로 부터 REQ 받지 않으면 답변할 게 없음
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		pass


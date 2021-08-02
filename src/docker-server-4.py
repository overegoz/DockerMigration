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
# --network="host" 일때만 의미있음
#my_ap_name = socket.gethostname()
# -------------------------------------------------------------------
print('{} started at {}!'.format(my_name, my_ap_name))
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

localPort = common.port[my_name]
#print("EdgeServer: ", localIP, ", ", localPort)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind((localIP, localPort)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

print('socket setup complete!')
# -------------------------------------------------------------------
# SIGINT 시그널 핸들러 등록
def handler(signum, frame):
	print(common.sigint_msg)
	sock.close()
	exit()

signal.signal(signal.SIGINT, handler)
# -------------------------------------------------------------------
# 실행 되었다는 것을 Logger에 알리기
common.send_log(sock, my_name, my_name, 
				common.str2(common.start_msg, str(sys.argv)))
# -------------------------------------------------------------------
# 프로파일에 따라서 사전 작업을 수행함
profile = int(sys.argv[2])
common.run_profile(my_name, profile)
print('pre-work done!')
# -------------------------------------------------------------------
# 서비스를 할 준비가 되었음을 AP에게 알림
# 프로파일에 따른 사전작업이 모두 완료되면, ES_READY 메시지를 보내라.
# 이를 위한 카운터 변수를 만들자
# 0 : 한번도 알리지 않음
# +10 : ES1이 AP1에게 알림
# +100 : ES2가 AP2에게 알림
# 즉, 110이면 (ES1 -> ) AP1, (ES2 -> )AP2에게 알림
notified = 0
print('{} is ready to serve!'.format(my_name))
# -------------------------------------------------------------------
#print('host name : ', socket.gethostname())
# -------------------------------------------------------------------
# 서비스를 시작
no_recv_cnt = 0  # recv 못한 경우 카운트
yes_recv_cnt = 0  # recv 성공적으로 받은 경우 카운트
while(True): 
	"""
	Edge서버는 두 가지 통신만 한다.
	1. [recv] AP를 통해서 받은 USER의 REQ 
		: AP는 USER가 보낸 메시지를 그대로 전달해 줌
		: USER SVCQ <숫자>
	2. [send] USER의 REQ에 대한 응답을 AP로 보내는 것
		: EdgeServer<서버번호> SVCR <같은 숫자>
	"""
	# 지금 어떤 AP에있는 ES인지를 매번 확인
	# - 지금은 --add-host 명령으로 /etc/hosts 파일의 내용을 기반으로 판단
	# - 근데, 환경변수를 사용해서 판단하는게 더 좋은듯?
	if False:
		# 환경 변수명이 ES2에서 기존의 ES1 이름으로 남아 있어서 안됨
		print('notified: ', notified)
		try:
			get_es_name = os.environ[common.ENV_ES_NAME]
			print('get_es_name: ', get_es_name)

			if get_es_name == common.edge_server1_name:  # 여기는 AP-1
				my_ap_name = common.ap1_name  # AP 이름 바꿔주고,
				my_name = common.edge_server1_name
				# 최초로 한번은 READY 메시지를 보내주자
				assert notified == 0 or notified == 10  # 이외의 다른 값은 될 수 없음
				if notified == 0:  # ES가 시작되고, 한번도 READY 메시지를 AP에게 보내지 않은 경우
					send_msg = common.str2(my_name, common.ES_READY)
					print('{} -> {} : {}'.format(my_name, my_ap_name, send_msg))
					common.udp_send(sock, my_name, my_ap_name, send_msg, common.SHORT_SLEEP)
					notified += 10
					print('notified: ', notified)

			elif get_es_name == common.edge_server2_name:  # 여기는 AP-2
				my_ap_name = common.ap2_name  # AP 이름 바꿔주고,
				my_name = common.edge_server2_name  # 내 이름 (ES)도 바꿔주자
				# 최초로 한번은 READY 메시지를 보내주자
				assert notified == 0 or notified == 10 or notified == 100 or notified == 110  # 이외의 다른 값은 될 수 없음
				if notified == 0 or notified == 10:  # AP2에서 최초 실행이거나(LR), migr 후에 AP2에서 실행되는 경우
					send_msg = common.str2(my_name, common.ES_READY)
					print('{} -> {} : {}'.format(my_name, my_ap_name, send_msg))
					common.udp_send(sock, my_name, my_ap_name, send_msg, common.SHORT_SLEEP)
					notified += 100
					print('notified: ', notified)	
			else:
				assert False, "잘못된 ENV_ES_NAME이 정의되어 있음"

		except:
			assert False, "ENV_ES_NAME 이 정의되어 있어야 함"
	else:
		try:
			# ap2_hostname은 migr 후 ES2번을 실행할 때만 정의된다
			_ = socket.gethostbyname(common.ap2_hostname)
			# ------------------------------------------------------
			# 오류가 없다면, 여기는 AP-2
			# ------------------------------------------------------
			my_ap_name = common.ap2_name  # AP 이름 바꿔주고,
			my_name = common.edge_server2_name  # 내 이름 (ES)도 바꿔주자
			# 최초로 한번은 READY 메시지를 보내주자
			assert notified == 10 or notified == 110
			if notified == 10:
				send_msg = common.str2(my_name, common.ES_READY)
				print('{} -> {} : {}'.format(my_name, my_ap_name, send_msg))
				common.udp_send(sock, my_name, my_ap_name, send_msg, common.SHORT_SLEEP)
				notified += 100
				print('notified: ', notified)	
		except:
			# ------------------------------------------------------
			# 오류가 있다면, 여기는 AP-1
			# ------------------------------------------------------
			my_ap_name = common.ap1_name
			my_name = common.edge_server1_name
			# 최초로 한번은 READY 메시지를 보내주자
			assert notified == 0 or notified == 10
			if notified == 0:
				send_msg = common.str2(my_name, common.ES_READY)
				print('{} -> {} : {}'.format(my_name, my_ap_name, send_msg))
				common.udp_send(sock, my_name, my_ap_name, send_msg, common.SHORT_SLEEP)
				notified += 10
				print('notified: ', notified)

	# 직접 연결된 AP로 부터 데이터 수신하기
	recv_msg, _ = common.udp_recv(sock, my_name, common.bufsiz, common.SHORT_SLEEP) 

	if len(recv_msg) > 0:
		yes_recv_cnt += 1
		print('recv: ', recv_msg)
		words = recv_msg.split(common.delim)

		# sender 정보가 맞는지 확인
		"""
		# migr 이후에는 맞지 않는 정보
		if words[0] != my_ap_name:
			common.send_log(sock, my_name, my_name, \
							common.str2("invalid-sender-name", recv_msg))
			assert False
		"""

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
	else:
		no_recv_cnt += 1

	if 	((no_recv_cnt + yes_recv_cnt) % 100) == 0: 
		print('recv : {}, no recv : {} on {} machine'.format(yes_recv_cnt, no_recv_cnt, my_ap_name))

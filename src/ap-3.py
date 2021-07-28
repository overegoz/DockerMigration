import socket 
import time
import signal, os, sys
import datetime
import common

"""
실행 방법
$ python3 ap-edge.py <이름> <ES 프로파일>
따라서, command line arg 개수는 총 3개 (코드이름 + 2개 인자)
<이름> : common에 정의된 AP의 이름 중 하나
<ES 프로파일> : 숫자번호
"""
# -------------------------------------------------------------------
# command line arg 처리
# -------------------------------------------------------------------
err_msg = ""
if len(sys.argv) != 3:
	# 인자 갯수가 정확하지 않음
	err_msg = "Need 2 args: <ap name> <profile>, but you entered " + str(sys.argv)
elif sys.argv[1] != common.ap1_name \
	 and sys.argv[1] != common.ap2_name:
	# AP 이름이 정확하지 않음
	err_msg = "Incorrect AP name! " + str(sys.argv[1])
elif int(sys.argv[2]) not in common.profile_ids:
	# 정의되지 않은 프로필 번호가 주어짐	
	err_msg = "Incorrect profile id! " + str(sys.argv[2])	
else:
	pass

if len(err_msg) > 0:
	# 오류가 있었다는 것임. 로그 전송 하지 않고, 터미널 출력하자
	assert False, "ERR MSG: " + err_msg
# -------------------------------------------------------------------
my_name = sys.argv[1]
my_edgeserver = ""
other_ap = ""
if my_name == common.ap1_name:
	my_edgeserver = common.edge_server1_name
	other_ap = common.ap2_name
elif my_name == common.ap2_name:
	my_edgeserver = common.edge_server2_name
	other_ap = common.ap1_name
else:
	assert False

assert len(my_edgeserver) > 0 and len(other_ap) > 0
# -------------------------------------------------------------------
# listen 소켓 생성
local_ip,local_port = common.ip[my_name], common.port[my_name]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기
# -------------------------------------------------------------------
# 실행 되었다는 것을 Logger에 알리기
common.send_log(sock, my_name, my_name, common.str2(common.start_msg,str(sys.argv)))
# -------------------------------------------------------------------
# 상태 정보를 기록할 변수들
profile = int(sys.argv[2])
user_associated = False
edge_server_ready = False
# -------------------------------------------------------------------
# Edge Server (Docker) 시작하기
if my_name == common.ap1_name:
	# AP-1은 시작과 동시에 ES 를 시작
	common.start_edgeserver(es_name=my_edgeserver, profile=profile)
	common.send_log(sock, my_name, common.edge_server1_name, 
					common.str2(common.start_msg, " (initial launch)"))
elif my_name == common.ap2_name:
	# AP2는 시작과 동시에 프로필을 시작할 필요 없음. 컨트롤러가 시키면 그 때 시작
	edge_server_ready = False
else:
	assert False
# -------------------------------------------------------------------
# 핸들러 등록
def handler(signum, frame):
	print(common.sigint_msg)
	sock.close()
	if edge_server_ready == True:
		common.stop_edgeserver(profile)
	exit()
	
signal.signal(signal.SIGINT, handler)
# -------------------------------------------------------------------
# 서비스 시작
delim = common.delim
while(True):
	# -------------------------------------------------------------------
	# 데이터 수신
	recv_msg, addr = common.udp_recv(sock, my_name, common.bufsiz, common.SHORT_SLEEP) 
	# -------------------------------------------------------------------
	if len(recv_msg) > 0:  # 수신한 데이터가 있으면...
		words = recv_msg.split(common.delim)
		#print(words)
		sender = words[0]
		cmd = words[1]

		if cmd == common.INFO_REQ:  # [AR1] 컨트롤러가 migr 관련 정보 요청
			assert sender == common.controller_name
			# [AS1] migr 기법 결정에 필요한 정보를 컨트롤러에게 전달해줌
			info = common.return_migr_info_ap1(profile)
			msg = common.str4(my_name, common.INFO_RES, profile, info)
			common.udp_send(sock, my_name, common.controller_name, msg, common.SHORT_SLEEP)
		elif cmd == common.MIGR_SRC:  # [AR2] migr 출발지, 시작!
			# profile : 시나리오 프로파일
			migr_tech = words[2]  # 마이그레이션 기법
			print('MIGR_SRC: ', migr_tech)
			print('미구현!!!')
			# other_ap : 마이그레이션 목적지
			pass  # todo 
		elif cmd == common.MIGR_DST:  # [AR3] migr 도착지, 시작!
			migr_tech = words[2]
			print('MIGR_DST: ', migr_tech)
			print('미구현!!!')

			# 테스트
			if migr_tech == common.MIGR_NONE:  # 프로필 1번
			- 구현하기

			# 스레드 만들어서 edge server를 시작해야 할 듯?

			# ES 준비가 완료되면 AP-1에게 알려서 AP-1의 ES를 종료토록 하기
			- 이 부분에 대한 msg 정의하기

			pass  # todo
		elif cmd == common.SVC_REQ:  # 서비스 요청 [AR4][AR9]
			assert sender == common.user_name or sender == other_ap
			send_msg = common.str3(my_name, words[1], words[2])
			if edge_server_ready == True:  # 나의 ES가 정상 동작함
				# [AS4.1][AS9.1] 수신 메시지를 edge server에게 전달해줌
				common.udp_send(sock, my_name, my_edgeserver, send_msg, common.SHORT_SLEEP)
			else:  # 나의 ES가 down 상태임
				# [AS4.2][AS9.2] 수신 메시지를 다른 AP에게 전달해줌
				print('[서비스 요청] 동작하는 ES가 없어서 다른 AP로 전달')
				common.udp_send(sock, my_name, other_ap, send_msg, common.SHORT_SLEEP)
		elif cmd == common.USER_HELLO:  # [AR5] 새로운 user가 접속했다
			assert user_associated == False  # user는 한명 뿐이거든...
			user_associated = True
			if edge_server_ready == True:
				cmd = common.ES_READY
				common.udp_send(sock, my_name, common.user_name, 
								common.str2(my_name, cmd), common.SHORT_SLEEP)
		elif cmd == common.USER_BYE:  # [AR6] 기존 user가 접속을 해제했다
			assert user_associated == True
			user_associated = False
		elif cmd == common.SVC_RES:  # [AR7][AR8][AR10] 사용자 요청에 대한 응답을 받았다
			assert sender == my_edgeserver or sender == other_ap
			# 응답 메시지 구성하기
			send_msg = common.str3(my_name, words[1], words[2])
			if user_associated == True:  # [AS7] 나에게 연결된 user로 보내기
				common.udp_send(sock, my_name, common.user_name, send_msg, common.SHORT_SLEEP)
				print('USER에게 전달: ', send_msg)
			else:  # [AS8] 다른 AP로 relay 해주기
				print('[서비스 응답] 연결된 사용자가 없어서 다른 AP로 전달')
				common.udp_send(sock, my_name, other_ap, send_msg, common.SHORT_SLEEP)
		elif cmd == common.ES_STOP:  # [AR11] edge server 정지하기
			pass  # todo
		elif cmd == common.ES_START:  # [AR12] edge server 시작하기
			pass  # todo
		elif cmd == common.ES_READY:  # [AR13] edge server가 서비스 가능한 상태로 변경되었음
			edge_server_ready = True
			if (my_name == common.ap1_name) and (user_associated == True):
				# [AS13] 이 때만 user에게 알려주기
				common.udp_send(sock, my_name, common.user_name, 
								common.str2(my_name, cmd), common.SHORT_SLEEP)
		elif cmd == common.USER_EXIT:
			user_associated = False  # [AR14] user가 아예 종료하고 떠나는 것
		else:
		    assert False
	else: 
		# 수신 데이터가 없으면, 아무 것도 할 게 없음
		pass
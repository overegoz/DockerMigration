from threading import Thread
import socket 
import time, datetime
import signal, os, sys
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
# migr에 필요한 디렉토리 생성
common.check_dirs(common.dir_list)
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
migr_type = ""
# -------------------------------------------------------------------
# Edge Server (Docker) 시작하기 // AP-1만 ES를 이때에 시작한다
edge_server_ready = None
if my_name == common.ap1_name:
	# AP-1은 시작과 동시에 ES 를 시작
	# 여기서는 thread 쓰지말자
	common.start_edgeserver(es_name=my_edgeserver, migr_type="no need", profile=profile)
	edge_server_ready = True
	common.send_log(sock, my_name, common.edge_server1_name, 
					common.str2(common.start_msg, " (initial launch)"))
elif my_name == common.ap2_name:
	# AP2는 시작과 동시에 프로필을 시작할 필요 없음. 컨트롤러가 시키면 그 때 시작
	edge_server_ready = False
else: 
	assert False
# -------------------------------------------------------------------
# 스레드 변수 
thr_start, thr_stop = None, None  # ES 시작용 스레드, ES 종료용 스레드
thr_migr = None  # MIGR-SRC에서 실행하는 작업을 위한 스레드
# -------------------------------------------------------------------
# 핸들러 등록
def handler(signum, frame):
	print(common.sigint_msg)
	sock.close()
	if edge_server_ready == True:
		common.stop_edgeserver(profile)  # 여기서는 thread 쓰지말자
	if thr_start is not None:
		thr_start.join()
	if thr_stop is not None:
		thr_stop.join()
	if thr_migr is not None:
		thr_migr.join()
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
		print('recv: ', recv_msg)
		words = recv_msg.split(common.delim)
		
		sender = words[0]
		cmd = words[1]

		if cmd == common.INFO_REQ:  # [AR1] 컨트롤러가 migr 관련 정보 요청
			assert sender == common.controller_name
			# [AS1] migr 기법 결정에 필요한 정보를 컨트롤러에게 전달해줌
			info = common.return_migr_info_ap1(profile)
			# <AP-X> <INFR> <프로파일 번호> <migr 판단에 필요한 정보, '-'로 구분>
			msg = common.str4(my_name, common.INFO_RES, str(profile), info)
			common.udp_send(sock, my_name, common.controller_name, msg, common.SHORT_SLEEP)
		elif cmd == common.MIGR_SRC:  # [AR2] migr 출발지, 시작! (참고: 마이그레이션 목적지는 other_ap)
			assert edge_server_ready == True
			assert len(migr_type) == 0

			# profile : 시나리오 프로파일
			migr_type = words[2]  # 마이그레이션 기법

			assert migr_type == common.MIGR_NONE or migr_type == common.MIGR_FC \
				or migr_type == common.MIGR_DC or migr_type == common.MIGR_LR
			
			print('MIGR 작업을 시작합니다 : {}'.format(migr_type))
			
			thr_migr = Thread(target=common.start_migr, \
								args=(sock, migr_type, my_name, other_ap, common.prof))
			thr_migr.start()
			# migr 시간 측정 : 로그에서, 여기서 부터 시간을 측정하면 됨.
			common.send_log(sock, my_name, my_name, common.str2("migr begins : ", migr_type))
		elif cmd == common.MIGR_DST:  # [AR3] migr 도착지, 시작! (참고: 마이그레이션 출발지는 other_ap)
			assert edge_server_ready == False
			assert len(migr_type) == 0

			migr_type = words[2]
			print('MIGR_DST: ', migr_type, ' (구현 미완료)')
			# 여기선, 이 타이밍에서는 딱히 해줄 게 없어 
			# base image를 pull 하도록 하자 => 프로파일용 img는 local img라서 pull 불가
		elif cmd == common.SVC_REQ:  # 서비스 요청 [AR4][AR9]
			assert sender == common.user_name or sender == other_ap
			send_msg = common.str3(my_name, words[1], words[2])
			if edge_server_ready == True:  # 나의 ES가 정상 동작함
				# [AS4.1][AS9.1] 수신 메시지를 edge server에게 전달해줌
				common.udp_send(sock, my_name, my_edgeserver, send_msg, common.SHORT_SLEEP)
				print('[서비스 요청] 나의 ES로 전달 {}/{}'.format(common.ip[my_edgeserver], 
																common.port[my_edgeserver]))
			else:  # 나의 ES가 down 상태임
				# [AS4.2][AS9.2] 수신 메시지를 다른 AP에게 전달해줌
				print('[서비스 요청] 동작하는 ES가 없어서 다른 AP로 전달')
				common.udp_send(sock, my_name, other_ap, send_msg, common.SHORT_SLEEP)
		elif cmd == common.USER_HELLO:  # [AR5] 새로운 user가 접속했다
			assert user_associated == False  # user는 한명 뿐이거든...
			user_associated = True
			if (my_name == common.ap1_name) and (edge_server_ready == True):
				# [AS13] 이 때만 user에게 알려주기 (user가 while-loop을 탈출할 수 있도록!)
				common.udp_send(sock, my_name, common.user_name, 
								common.str2(my_name, common.ES_READY), common.SHORT_SLEEP)
		elif cmd == common.USER_BYE:  # [AR6] 기존 user가 접속을 해제했다
			assert user_associated == True
			user_associated = False
		elif cmd == common.SVC_RES:  # [AR7][AR8][AR10] 사용자 요청에 대한 응답을 받았다
			assert sender == my_edgeserver or sender == other_ap
			# 응답 메시지 구성하기
			send_msg = common.str3(my_name, words[1], words[2])
			if user_associated == True:  # [AS7] 나에게 연결된 user로 보내기
				common.udp_send(sock, my_name, common.user_name, send_msg, common.SHORT_SLEEP)
				print('[서비스 응답] 직접 연결된 USER에게 전달: ', send_msg)
			else:  # [AS8] 다른 AP로 relay 해주기
				print('[서비스 응답] 연결된 사용자가 없어서 다른 AP로 전달')
				common.udp_send(sock, my_name, other_ap, send_msg, common.SHORT_SLEEP)
		elif cmd == common.ES_STOP:  # [AR11] edge server 정지하기
			# AP-2에서 ES가 준비 완료되면, AP-1에게 이 메시지를 전해줄거야...
			print("ES 종료 시작!")
			edge_server_ready = False  # 이걸 먼저하자. ES STOP에 시간이 좀 걸리더라...
			# ES 종료는 스레드로 처리하자 // join은 시그널 핸들러에서...
			thr_stop = Thread(target=common.stop_edgeserver, args=(profile,))  # 1 arg 일때는 컴마(,)
			thr_stop.start()
		elif cmd == common.ES_START:  # [AR12] edge server 시작하기
			# AP-1에서 migr에 필요한 데이터를 AP-2로 전송 완료한 후, AP-1이 AP-2에게 보내주는 메시지
			assert sender == other_ap
			print("ES 를 시작합니다")	
			thr_start = Thread(target=common.start_edgeserver, args=(my_edgeserver, migr_type, profile))
			thr_start.start()
			# edge_server_ready 는 common.ES_READY 받으면 True로 설정
		elif cmd == common.ES_READY:  # [AR13] edge svr가 서비스 가능 상태로 변경되었음을 알려줌
			edge_server_ready = True
			if (my_name == common.ap1_name) and (user_associated == True):
				# 프로그램을 처음 시작할때, AP-1에게 접속한 user에게 보내주는 메시지
				# [AS13] 이 때만 user에게 알려주기 (user가 while-loop을 탈출할 수 있도록!)
				# 이후로는 user에게 알려줄 필요 없다
				common.udp_send(sock, my_name, common.user_name, 
								common.str2(my_name, cmd), common.SHORT_SLEEP)
			if my_name == common.ap2_name:  # migr 완료
				# migr 완료 로그 남기기
				# migr 시간 측정 : 로그에서, 여기까지 소요된 시간을 측정하면 됨.
				common.send_log(sock, my_name, my_name, "migr finished")
				# [AS11] AP-1의 ES를 종료하라고 알려줘야지?
				common.udp_send(sock, my_name, other_ap,
								common.str2(my_name, common.ES_STOP), common.SHORT_SLEEP)
		elif cmd == common.USER_EXIT:
			user_associated = False  # [AR14] user가 아예 종료하고 떠나는 것
		else:
		    assert False
	else: 
		# 수신 데이터가 없으면, 아무 것도 할 게 없음
		pass
"""
EdgeServer 즉 도커 컨테이너에서 실행할 코드이다.
"""
from threading import Thread
import socket, signal, os, sys
import datetime, time
import common
import multiprocessing

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
	common.send_log(None, sock, "EdgeServer-X", "EdgeServer-X", err_msg)
	sock.close()
	exit()  # 즉시 종료
# -------------------------------------------------------------------
manager = multiprocessing.Manager()  # 공유 변수를 위한 매니저
shared_dict = manager.dict()
# -------------------------------------------------------------------
shared_dict['my_name'] = sys.argv[1]
#my_name = sys.argv[1]
shared_dict['my_ap_name'] = ""
#my_ap_name = ""
if shared_dict['my_name'] == common.edge_server1_name:
	shared_dict['my_ap_name'] = common.ap1_name
elif shared_dict['my_name'] == common.edge_server2_name:
	shared_dict['my_ap_name'] = common.ap2_name
else:
	assert False
# -------------------------------------------------------------------
# --network="host" 일때만 의미있음
#my_ap_name = socket.gethostname()
# -------------------------------------------------------------------
if common.ENABLE_DEB_MSG:
	print('{} started at {}!'.format(shared_dict['my_name'], shared_dict['my_ap_name']))
# -------------------------------------------------------------------
profile = int(sys.argv[2])
migr_type = common.prof.get_predetermined_migr(profile)
# -------------------------------------------------------------------
"""
- 컨테이너는 기본적으로 0.0.0.0 IP 주소를 가진다. 따라서 서버 IP 주소를
0.0.0.0 으로 설정해 줘야 한다.
- 포트 포워딩은 서버 수신 포트만 해 주면 된다.
"""
# listen 소켓 생성
if( profile == -1 ):  # 도커 없이 실행하는, 테스트용 run
	localIP = common.ip[shared_dict['my_name']]
else:
	localIP = common.ip_fake[shared_dict['my_name']]

localPort = common.port[shared_dict['my_name']]
#print("EdgeServer: ", localIP, ", ", localPort)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind((localIP, localPort)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

if common.ENABLE_DEB_MSG:
	print('socket setup complete!')
# -------------------------------------------------------------------
# 스레드 변수 
udp_send_threads = []  # 위에서 manager.list 객체로 선언해서 공유하도록...
# -------------------------------------------------------------------
# 병렬처리
process_jobs = []
shared_dict['thr_action'] = None
# -------------------------------------------------------------------
# SIGINT 시그널 핸들러 등록... 
# container stop 하면 SIGTERM -> SIGKILL 전달된다
def handler(signum, frame):
	print(common.sigint_msg)
	shared_dict['sock'].close()
	if shared_dict['thr_action'] is not None:
		shared_dict['thr_action'].join()

	for proc in process_jobs:
		proc.join()

	for th in udp_send_threads:
		th.join()

	exit()


#signal.signal(signal.SIGINT, handler)
original_handler = signal.signal(signal.SIGTERM, handler)  # container stop 하면 SIGTERM -> SIGKILL 전달된다
# -------------------------------------------------------------------
# 실행 되었다는 것을 Logger에 알리기
common.send_log(None, sock, shared_dict['my_name'], shared_dict['my_name'], 
				common.str2(common.start_msg, str(sys.argv)))
# -------------------------------------------------------------------
# 서비스를 할 준비가 되었음을 AP에게 알림
# 프로파일에 따른 사전작업이 모두 완료되면, ES_READY 메시지를 보내라.
# 이를 위한 카운터 변수를 만들자
# 0 : 한번도 알리지 않음
# +10 : ES1이 AP1에게 알림
# +100 : ES2가 AP2에게 알림
# 즉, 110이면 (ES1 -> ) AP1, (ES2 -> )AP2에게 알림
shared_dict['notified'] = 0
if common.ENABLE_DEB_MSG:
	print('{} is ready to serve!'.format(shared_dict['my_name']))
# -------------------------------------------------------------------
#print('host name : ', socket.gethostname())
# -------------------------------------------------------------------
# 서비스를 시작
no_recv_cnt = 0  # recv 못한 경우 카운트
yes_recv_cnt = 0  # recv 성공적으로 받은 경우 카운트

# -------------------------------------------------------------------
# host를 확인하는 것을 스레드로 구성
# 이것 때문에 ES-1에서의 딜레이가 불안정적이 되는 것 같아서...
shared_dict['run_action_profile'] = 0

def hostcheck(shared_dict):
	# 이 함수는 별도의 프로세스로 생성되는 것이다.
	# 시그널 핸들러를 원래 값으로 돌려놓자. 종료 작업은 parent process가 처리함
	signal.signal(signal.SIGTERM, original_handler)
	#global notified, my_ap_name, my_name, thr_action
	# 지금 어떤 AP에있는 ES인지를 매번 확인
	# - 지금은 --add-host 명령으로 /etc/hosts 파일의 내용을 기반으로 판단
	# - 환경변수를 사용해서 판단하려고 했는데, ES1에서 정의한 env 이름이 ES2에서
	#   업데이트 되지 않아서, 그냥 기존의 add-hosts 방법을 사용하기로 함
	while True:
		time.sleep(0.100)  # CPU 과도한 사용을 막기위함
		try:
			#print('1')
			# ap2_hostname은 migr 후 ES2번을 실행할 때만 정의된다
			_ = socket.gethostbyname(common.ap2_hostname)
			#print('2')
			# ------------------------------------------------------
			# 오류가 없다면, 여기는 AP-2
			# ------------------------------------------------------
			#print('gethostbyname : success')
			shared_dict['my_ap_name'] = common.ap2_name  # AP 이름 바꿔주고,
			shared_dict['my_name'] = common.edge_server2_name  # 내 이름 (ES)도 바꿔주자
			#
			# 아래의 READY 메시지 전송 및 지정작업 수행은 main 함수로 옮겼음
			# 여기서 실행하면 병렬 처리가 되 버리니까, 순차처리를 하도록 main으로 코드 이동
			#
			# 최초로 한번은 READY 메시지를 보내주자
			if shared_dict['notified'] == 0 or shared_dict['notified'] == 10:
				shared_dict['notified'] += 100
				if common.ENABLE_DEB_MSG:
					print('notified: ', shared_dict['notified'])

				# Log-Replay 경우 : AP2는 main 함수의 while에서 '스레드 없이' 지정된 작업 수행
				shared_dict['run_action_profile'] = 1
				
		except socket.gaierror:  # socket.gethostbyname 함수가 던지는 예외(getaddrinfo failed)
			# ------------------------------------------------------
			# 오류가 있다면, 여기는 AP-1
			# ------------------------------------------------------
			#print('gethostbyname : failed')
			#print('3')
			shared_dict['my_ap_name'] = common.ap1_name
			shared_dict['my_name'] = common.edge_server1_name
			#print('4')
			#assert notified == 0 or notified == 10
			if shared_dict['notified'] == 0:
				shared_dict['notified'] += 10
				#print('5')
				if common.ENABLE_DEB_MSG:
					print('notified: ', shared_dict['notified'])

				#print('6')

				# AP1은 지정된 작업을 병렬적으로 수행
				# 여기 코드는 어차피 multiprocessing으로 처리되니까, 그냥 실행하면 됨
				print('run action profile with parallelism')
				common.action_profile(shared_dict['my_name'], profile)
				#print('7')
				# (action_profile 리턴을 기다리지 않고) AP에게 READY 메시지 보내기
				# 최초로 한번은 READY 메시지를 보냄
				#print('8')

				send_msg = common.str2(shared_dict['my_name'], common.ES_READY)
				if common.ENABLE_DEB_MSG:
					print('{} -> {} : {}'.format(shared_dict['my_name'], shared_dict['my_ap_name'], send_msg))

				# 소켓을 매번 새로 만들자! my_name 변경 가능성도 있으니까, 매번 만드는 걸로
				localPort = common.TEMP_PORT_DOCKER
				print('hostcheck: ', localPort)
				localIP = common.ip_fake[shared_dict['my_name']]
				print('hostcheck: ', localIP)
				sock_fork = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
				sock_fork.bind((localIP, localPort)) 
				#sock.setblocking(0)  # non-blocking socket으로 만들기

				thrr = common.udp_send(sock_fork, shared_dict['my_name'], 
										shared_dict['my_ap_name'], send_msg, common.SHORT_SLEEP)	
				thrr.join()
				sock_fork.close()
		except:
			print('알려지지 않은 예외?')



# -------------------------------------------------------------------
# host를 확인하는 것을 멀티-프로세스로 구성
# 이것 때문에, 반복적으로 인터럽트 걸려서 수행 시간에 지장을 줄 수 있으니까...
p = multiprocessing.Process(target=hostcheck, args=(shared_dict,))
process_jobs.append(p)
p.start()

"""
multiprocessing 을 사용하는 경우에는 main을 써서 entry point를 보호해야
한다는 말을 들었는데, 정확히 무슨 의미인지는 모르겠지만, 일단 써 보자
"""
if __name__ == "__main__":
	while(True): 
		# print(os.environ.get(common.ENV_MIGR_TYPE))  # 이건 절대 안되는구만...
		"""
		Edge서버는 두 가지 통신만 한다.
		1. [recv] AP를 통해서 받은 USER의 REQ 
			: AP는 USER가 보낸 메시지를 그대로 전달해 줌
			: USER SVCQ <숫자>
		2. [send] USER의 REQ에 대한 응답을 AP로 보내는 것
			: EdgeServer<서버번호> SVCR <같은 숫자>
		"""
		# ........................................................................
		# Log-Replay 경우 : AP2는 '스레드 없이' 지정된 작업 1회만 수행
		if shared_dict['my_name'] == common.edge_server2_name:
			if shared_dict['run_action_profile'] == 1:  # 1회만 수행하도록...
				shared_dict['run_action_profile'] = 0  # 앞으로는 수행 안함
				
				if migr_type == common.MIGR_LR:  # LR 일때만...
					print('병렬처리 없이 action profile 코드를 실행합니다.')
					common.action_profile(shared_dict['my_name'], profile)
				else:
					print('action profile 실행하지 않습니다')

				# 'Log-Replay 작업이 완료되면' READY 메시지를 AP2에게 보내주기
				send_msg = common.str2(shared_dict['my_name'], common.ES_READY)
				if common.ENABLE_DEB_MSG:
					print('{} -> {} : {}'.format(shared_dict['my_name'], shared_dict['my_ap_name'], send_msg))

				thrr = common.udp_send(sock, shared_dict['my_name'], 
										shared_dict['my_ap_name'], send_msg, common.SHORT_SLEEP)
				udp_send_threads.append(thrr)

		# ........................................................................
		# 직접 연결된 AP로 부터 데이터 수신하기
		recv_msg, _ = common.udp_recv(sock, shared_dict['my_name'], common.bufsiz, common.SHORT_SLEEP) 

		if len(recv_msg) > 0:
			yes_recv_cnt += 1
			if common.ENABLE_DEB_MSG:
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

			# 오류 처리: [ER1][ER2] 서비스 요청 메시지가 맞는지 확인
			if words[1] != common.SVC_REQ:
				common.send_log(None, sock, shared_dict['my_name'], shared_dict['my_name'], \
								common.str2("invalid-command-received", recv_msg))
				assert False

			# 오류 처리: 수신 메시지가 형식에 맞는지 확인하기
			if len(words) != 3:
				common.send_log(None, sock, shared_dict['my_name'], shared_dict['my_name'], 
								common.str2("wrong-msg-format", recv_msg))
				assert False

			# 직접 연결된 AP에게 전송할 메시지 준비하기
			counter = words[2]
			send_msg = common.str3(shared_dict['my_name'], common.SVC_RES, counter)
			# [ES1][ES2] 직접 연결된 AP에게 메시지 전송
			thrr = common.udp_send(sock, shared_dict['my_name'], 
									shared_dict['my_ap_name'], send_msg, common.SHORT_SLEEP)
			udp_send_threads.append(thrr)
		else:
			no_recv_cnt += 1

		if 	((no_recv_cnt + yes_recv_cnt) % 1000) == 0: 
			if common.ENABLE_DEB_MSG:
				print('recv : {}, no recv : {} on {} machine'.format(yes_recv_cnt, no_recv_cnt, shared_dict['my_ap_name']))

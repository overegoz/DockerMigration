"""
- 공통으로 사용하는 값을 정의
- 참고: 도커가 인식하는 자신의 IP는 0.0.0.0이다
"""
import time, datetime, socket, sys, os
from Profile import Profile

# -------------------------------------------------------------------
# 총 4대의 VM을 사용하자
# 1. controller + logger
# 2. user
# 3. ap-1 (+ EdgeServer 1)
# 4. ap-2 (+ EdgeServer 2)
# -------------------------------------------------------------------
# 이름 정의하기
controller_name = "CTRL"
logger_name = "LOGR"
user_name = "USER"
ap1_name = "AP-1"
ap2_name = "AP-2"
edge_server1_name = "EdgeServer-1"
edge_server2_name = "EdgeServer-2"
# -------------------------------------------------------------------
# ip table
"""
ip = {controller_name : "127.0.0.1",
		logger_name : "127.0.0.1",
		user_name : "127.0.0.1",
		ap1_name : "127.0.0.1",
		ap2_name : "127.0.0.1",
		edge_server1_name : "127.0.0.1",
		edge_server2_name : "127.0.0.1"}
"""
ip = {controller_name : "192.168.0.2",
		logger_name : "192.168.0.2",
		user_name : "192.168.0.2",
		ap1_name : "192.168.0.2",
		ap2_name : "192.168.0.2",
		edge_server1_name : "192.168.0.113",
		edge_server2_name : "192.168.0.114"}

# 도커가 인식하는 자신의 IP는 0.0.0.0이다        
ip_fake = {edge_server1_name : "0.0.0.0",
		edge_server2_name : "0.0.0.0"}
# -------------------------------------------------------------------
# port number
port = {controller_name : 20000,
		logger_name : 20001,
		user_name : 20002,
		ap1_name : 20003,
		ap2_name : 20004,
		edge_server1_name : 20005,
		edge_server2_name : 20006}
# -------------------------------------------------------------------
# directory
account = "daniel"
base_dir = "/home/" + account + "/migration/"
checkpoint_dir = base_dir + "CheckPoints/"
fullcopy_dir = base_dir + "FullCopyImages/"
diffcopy_dir = base_dir + "DiffCopyFiles/"
logreplay_dir = base_dir + "LogReplayRecords/"
# -------------------------------------------------------------------
# 메시지 정의
sigint_msg = "SIGINT handler called! Terminating...\n"
start_msg = "start"
# -------------------------------------------------------------------
# COMMAND 정의
SVC_REQ = "SVCQ"  # EdgeServer에 서비스를 요청하는 메시지
SVC_RES = "SVCR"
USER_HELLO = "HELO"  # user가 ap에 association 한 직후 보내는 메시지
USER_BYE = "BYEE"  # user가 ap에서 떠나가기 직전에 보내는 메시지
USER_EXIT = "EXIT"  # user가 아예 종료하고 떠나는 것
MIGR_FC = "FULL-COPY"  # migr 기법 1
MIGR_DC = "DIFF-COPY"  # migr 기법 2
MIGR_LR = "LOG-REPLAY"  # migr 기법 3
MIGR_AUTO = "AUTO"
INFO_REQ = "INFQ"  # migr 기법 판단에 필요한 정보 요청 (컨트롤러 > old AP)
INFO_RES = "INFR"  # migr 기법 판단에 필요한 정보 회신 (old AP > 컨트롤러)
MIGR_SRC = "MIGR-SRC"  # migr 출발지로써, 준비하고 실행하라!
MIGR_DST = "MIGR-DST"  # migr 목적지로써, 준비하고 실행하라!
ES_START = "ES-START"  # Edge Server 구동하기
ES_STOP = "ES-STOP"  # Edge Server 정지하기
ES_READY = "ES-READY"  # Edge Server 가 ready 상태가 되고, 서비스 가능함
# -------------------------------------------------------------------
# 상수 정의
bufsiz = 1024
delim = " "
SHORT_SLEEP = 0.1
USER_REQ_INTERVAL = 1.0
USER_HANDOVER_DELAY = 1.0
INTMAX = sys.maxsize  # 참고: 파이썬2 에서는 sys.maxint
weight = 10
# -------------------------------------------------------------------
# 어떤 시나리오로 실험할 것인지를 프로필로 구성하자
# . 프로필 -1번 : 도커 없이 실행
# . 프로필 0번 : 도커 있지만 migr 없음
prof = Profile()
profile_ids = list(range(prof.id_min(), prof.id_max()+1))
# -------------------------------------------------------------------
# 공통으로 사용하는 함수를 정의하기
def get_key_by_value(tab, value):
	return list(tab.keys())[list(tab.values()).index(value)]
"""
로그 형식
<시간> <로그 작성자> <이번 이벤트에 대한 상대방> <메시지>
"""
def str2(a,b):
	return a + delim + b

def str3(a,b,c):
	return a + delim + b + delim + c

def str4(a,b,c,d):
	return a + delim + b + delim + c + delim + d

def get_now():  # 현재 시간을 문자열로 리턴
	return datetime.datetime.now().strftime("%Y-%m-%m-%H-%M-%S-%f")
	
def send_log(sock, me, you, msg):
	# 로그 메시지 만들기
	log = get_now() + delim + me + delim + you + delim + msg
	# Logger에게 전송하기
	# udp_send(sock, me, logger_name, log, SHORT_SLEEP)  # 이렇게 하면 무한 루프
	sock.sendto(log.encode(), (ip[logger_name], port[logger_name]))


def udp_send(sock, me, you, msg, t):
	time.sleep(t)
	# 메시지 보내기
	#print("msg : ", msg)
	#print("you : ", you)
	#print(msg, ip[you], port[you])
	sock.sendto(msg.encode(), (ip[you], port[you]))

	# 로그에 기록하기
	send_log(sock, me, you, msg + delim + "(sent)")

def udp_recv(sock, me, bufsize, t):
	time.sleep(t)
	msg, addr = "", ""
	try:
		# 메시지 받기
		bytes, addr = sock.recvfrom(bufsize)
		# 수신 데이터 출력하기, decode 해서 string객체로 변환
		msg = bytes.decode()
		# 로그에 기록하기
		if me != logger_name:  # 내가 LOGGER가 아닌 경우에만...
			send_log(sock, me, addr[0], msg + delim + "(recvd)")

	except socket.error:
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		msg, addr = "", ""

	return msg, addr


def run_profile(my_name, p):
	"""
	프로파일 번호에 따라서 사전에 정의된 동작을 수행함
	- my_name = EdgeServer1이면 최초에 실행한것이고, 
				EdgeServer2이면 migr 으로 실행된 것이다.
	- p : 프로파일 번호            
	"""	    
	if p <= 0:
		 return  # 테스트

def start_edgeserver(es_name, profile):
	"""
	- profile : 어떤 프로파일을 적용할지 (base image 이름도 포함)
	- ap1이면 최초로 실행하는 것이고, ap2이면 migr 으로 실행하는 것임
	"""
	if profile <= 0:  # 테스트 용
		return

	my_port = port[es_name]
	cont_name = prof.get_cont_name(profile)
	if es_name == edge_server1_name:  # 최초로 실행하는 것
		img_name = prof.get_img_name_ap1(profile)
	elif es_name == edge_server2_name:  # migr 으로 실행하는 것
		img_name = prof.get_img_name_ap2(profile)
	else:
		assert False

	cmd = 'docker run -p {}:{} --name {} {}'.format(my_port,my_port,cont_name,img_name)
	os.system(cmd)

def stop_edgeserver(profile):
	# profile에 base image 이름을 포함
	pass

def migrate():
	pass

def return_migr_info_ap1(p):
	"""
	프로파일 번호에 따라서, 어떤 정보를 컨트롤러에 리턴할지 미리 정해놓자
	리스트 형태로 만들고, 주어진 인덱스에 맞는 값을 리턴하도록 구현하자
	"""
	if p == -1:
		return "1 2 3 4 5 6"  # test

	C_sec,l_diff_bits,l_check_bits,l_log_bits,t_replay_sec,th_bps,force \
	= prof.p1_info()

	return str(C_sec) + delim + \
			str(l_diff_bits) + delim + \
			str(l_check_bits) + delim + \
			str(l_log_bits) + delim + \
			str(t_replay_sec) + delim + \
			str(th_bps)

def get_best_migr(infos, w, force):
	if force == MIGR_AUTO:
		info = infos.split(delim)
		C_s = float(info[0]) * 1.0
		l_diff_bit = float(info[1]) * 1.0
		l_check_bit = float(info[2]) * 1.0
		l_log_bit = float(info[3]) * 1.0
		t_replay_s = float(info[4]) * 1.0
		th_bps = float(info[5]) * 1.0
		# -------------------------------------------------
		dc_mig_time = C_s + l_diff_bit / th_bps + l_check_bit / th_bps
		dc_traffic = l_diff_bit + l_check_bit
		dc_cost = dc_mig_time + w * dc_traffic
		# -------------------------------------------------
		lr_mig_time = C_s + l_log_bit / th_bps + t_replay_s
		lr_traffic = l_log_bit
		lr_cost = lr_mig_time + w * lr_traffic
		# -------------------------------------------------
		if dc_cost <= lr_cost:
			return MIGR_DC
		elif lr_cost <= dc_cost:
			return MIGR_LR
		else:
			assert False
			return ""
	else:
		assert force == MIGR_FC or force == MIGR_DC or force == MIGR_LR
		return force
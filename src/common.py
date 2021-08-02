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
ap1_hostname = "docker-1"
ap2_hostname = "docker-2"
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
LOCAL_PC_IP = "192.168.0.2"
VM1_IP = "192.168.0.116"
VM2_IP = "192.168.0.117"
ip = {controller_name : LOCAL_PC_IP,
		logger_name : LOCAL_PC_IP,
		user_name : LOCAL_PC_IP,
		ap1_name : VM1_IP,
		ap1_hostname : VM1_IP,
		ap2_name : VM2_IP,
		ap2_hostname : VM2_IP,
		edge_server1_name : "127.0.0.1",  # ES1은 AP1 와 공존함
		edge_server2_name : "127.0.0.1"}   # ES2는 AP2와 공존함

# 도커가 인식하는 자신의 IP는 0.0.0.0이다        
# --network="host" 옵션을 사용해도 0.0.0.0을 사용해야 한다
ip_fake = {edge_server1_name : "0.0.0.0",
			edge_server2_name : "0.0.0.0"}

# -------------------------------------------------------------------
# port number
AP_PORT = 11003
ES_PORT = 11005
port = {controller_name : 11000,
		logger_name : 11001,
		user_name : 11002,
		ap1_name : AP_PORT,
		ap1_hostname : AP_PORT,
		ap2_name : AP_PORT,
		ap2_hostname : AP_PORT,
		edge_server1_name : ES_PORT,
		edge_server2_name : ES_PORT}
# -------------------------------------------------------------------
# directory
account = "daniel"
base_dir = "/home/" + account + "/migration/"
# checkpoint 이외에 복사해야 하는 파일을 저장하기 위한 폴더
fc_file_dir = base_dir + "FullCopyImages/"
dc_file_dir = base_dir + "DiffCopyFiles/"
lr_file_dir = base_dir + "LogReplayRecords/"
# checkpoint 를 저장하기 위한 폴더
fc_cp_dir = base_dir + "FC-CheckPoints/"
dc_cp_dir = base_dir + "DC-CheckPoints/"
lr_cp_dir = None  # LR는 checkpoint가 필요 없음
# 디렉토리 생성 코드는 AP에서 수행
dir_list = [fc_file_dir,dc_file_dir,lr_file_dir,fc_cp_dir,dc_cp_dir]
def check_dirs(dlist):
	for this_dir in dlist:
		if os.path.isdir(this_dir) == False:  # 존재하지 않으면
			os.makedirs(this_dir)  # 폴더 및 그 경로에 존재하는 폴더까지 생성
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
MIGR_NONE = "MIGR-NONE"
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
delimD = "-"
SHORT_SLEEP = 0.05
USER_REQ_INTERVAL = 1.0
USER_HANDOVER_DELAY = 1.0
INTMAX = sys.maxsize  # 참고: 파이썬2 에서는 sys.maxint
weight = 10  # 최적의 migr 기법 선택 시, 가중치
ENV_ES_NAME="EDGE_SERVER_NAME"  # 환경변수로 사용할 변수명
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
	return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
	
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
	if me == edge_server1_name or me == edge_server2_name:
		print('send: {} -> {}, {}, {}, {}'.format(me, you, msg, ip[you], port[you]))

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

def run_profile(es_name, profile):
	"""
	프로파일 번호에 따라서 사전에 정의된 동작을 수행함
	- es_name = EdgeServer1이면 최초에 실행한것이고, 
				EdgeServer2이면 migr 으로 실행된 것이다.
	- profile : 프로파일 번호            
	"""	    
	if profile <= 0:
		pass  # 테스트
	elif profile == 1:
		pass  # 할 일 없음 없음
	else:
		pass
	
def start_edgeserver(es_name, migr_type, profile):
	"""
	- profile : 어떤 프로파일을 적용할지 (base image 이름도 포함)
	- ap1이면 최초로 실행하는 것이고, ap2이면 migr 으로 실행하는 것임
	- 도커 실행할 때, remove 옵션 넣지말자
	- 도커 실행할 때, udp 없으면 안되 ㅠㅠ
	"""
	if profile <= 0:  # 테스트 용
		return

	my_port = port[es_name]
	cont_name = prof.get_cont_name(profile)
	if es_name == edge_server1_name:  # 최초로 실행하는 것
		img_name = prof.get_img_name_ap1(profile)

		#cmd = 'docker run -p {}:{}/udp -d --name {} {}'.format(my_port,my_port,cont_name,img_name)
		# 여기서는 ap1_hostname만 정의되어 있고, ap2_hostname은 없음
		if False:
			# 환경 변수명이 ES2에서 기존의 ES1 이름으로 남아 있어서 안됨
			cmd = 'docker run -e "TZ=Asia/Seoul" -e "{}={}" -p {}:{}/udp -d --name {} {}'.format(ENV_ES_NAME,es_name,my_port,my_port,cont_name,img_name)
		else:
			cmd = 'docker run -e "TZ=Asia/Seoul" --add-host {}:{} -p {}:{}/udp -d --name {} {}'.format(ap1_hostname,ip[ap1_hostname],my_port,my_port,cont_name,img_name)

		#cmd = 'docker run --network="host" -d --name {} {}'.format(cont_name,img_name)
		print(cmd)
		os.system(cmd)
	elif es_name == edge_server2_name:  # migr 으로 실행하는 것
		img_name = prof.get_img_name_ap2(profile)

		if migr_type == MIGR_NONE:
			#cmd = 'docker run -e "TZ=Asia/Seoul" -p {}:{}/udp -d --name {} {}'.format(my_port,my_port,cont_name,img_name)
			cmd = 'docker run -e "TZ=Asia/Seoul" -e "{}={}" -p {}:{}/udp -d --name {} {}'.format(ENV_ES_NAME,es_name,my_port,my_port,cont_name,img_name)
			#cmd = 'docker run --network="host" -d --name {} {}'.format(cont_name,img_name)
			print(cmd)
			os.system(cmd)
		elif migr_type == MIGR_FC:
			# 1. tar 파일로부터 이미지 불러오기
			print('FC (1/3)-이미지 불러오기')
			cmd = 'docker load -i {}.tar'.format(fc_file_dir + cont_name)
			print(cmd)
			os.system(cmd)

			# 2. 컨테이너 생성 (실행 안함)
			print('FC (2/3)-컨테이너 생성(실행 안함)')
			#cmd = 'docker create -p {}:{}/udp --name {} {}'.format(my_port,my_port,cont_name,img_name)
			# 여기서는 ap2_hostname이 정의되어 있다
			if False:
				# 환경 변수명이 ES2에서 기존의 ES1 이름으로 남아 있어서 안됨
				cmd = 'docker create -e "TZ=Asia/Seoul" -e "{}={}" -p {}:{}/udp --name {} {}'.format(ENV_ES_NAME,es_name,my_port,my_port,cont_name,img_name)
			else:
				cmd = 'docker create -e "TZ=Asia/Seoul" --add-host {}:{} -p {}:{}/udp --name {} {}'.format(ap2_hostname,ip[ap2_hostname],my_port,my_port,cont_name,img_name)

			#cmd = 'docker create --network="host" --name {} {}'.format(cont_name,img_name)
			print(cmd)
			os.system(cmd)

			# 3. 체크포인트로 컨테이너 실행
			print('FC (3/3)-컨테이너 실행 + 체크포인트')
			cp_name = prof.get_checkpoint_name(profile)
			cmd = 'docker start --checkpoint-dir={} --checkpoint={} {}'.format(fc_cp_dir, cp_name, cont_name)
			print(cmd)
			os.system(cmd)
		elif migr_type == MIGR_DC:
			# 1. 컨테니어 생성 (실행 안함)
			print('DC (1/3)-컨테이너 생성(실행 안함)')
			if False:
				# 환경 변수명이 ES2에서 기존의 ES1 이름으로 남아 있어서 안됨
				cmd = 'docker create -e "TZ=Asia/Seoul" -e "{}={}" -p {}:{}/udp --name {} {}'.format(ENV_ES_NAME,es_name,my_port,my_port,cont_name,img_name)
			else:
				cmd = 'docker create -e "TZ=Asia/Seoul" --add-host {}:{} -p {}:{}/udp --name {} {}'.format(ap2_hostname,ip[ap2_hostname],my_port,my_port,cont_name,img_name)

			print(cmd)
			os.system(cmd)

			# 2. diff 파일을 컨테이너에 복사해 넣기
			print('DC (2/3)-수신한 diff 파일을 복사해넣기')
			# 2.1 diff 절대경로 얻기
			output_filename = 'diff-dst-dir-{}.txt'.format(cont_name)
			cmd = 'docker inspect --format="{}" {} > {}'.format('{{.GraphDriver.Data.UpperDir}}', cont_name, output_filename)
			os.system(cmd)  # diff 절대경로를 파일에 기록
			fp = open(output_filename, 'r')
			diff_dst_dir = fp.readline()  # 파일에서 diff 절대경로명 획득
			diff_dst_dir = diff_dst_dir.rstrip()  # 마지막에 '\n'이 붙는데, 이거 제거하기
			fp.close()

			# 2.2 전송받은 폴더내의 파일을 diff 절대경로에 복사해넣기
			diff_src_dir = dc_file_dir + prof.get_final_dir_name(profile)

			# 수신받은 diff 파일을 UpperDir(=diff) 폴더에 그대로 복사해 넣자; 루트 권한 필요
			cmd = 'cp -r {}/* {}/'.format(diff_src_dir, diff_dst_dir)
			os.system(cmd)			

			# 3. 체크 포인트로 컨테이너 실행
			print('DC (3/3)-컨테이너 실행 + 체크포인트')
			cp_name = prof.get_checkpoint_name(profile)
			cmd = 'docker start --checkpoint-dir={} --checkpoint={} {}'.format(dc_cp_dir, cp_name, cont_name)
			print(cmd)
			os.system(cmd)
			pass
		elif migr_type == MIGR_LR:  # 사전에 준비된 새로운 img를 실행하는 것
			#로그 파일 수신 완료되면, 사전에 준비된 이미지를 실행하자
			#베이스 이미지에서 log를 모두 replay 하는 시나리오니까, docker img build 를 여기서 할 필요 없음
			pass
		else:
			assert False, "잘못된 MIGR 기법 : {}".format(migr_type)
	else:
		assert False, "잘못된 ES 이름 : {}".format(es_name)	

	print("EdgeServer를 시작 시켰습니다")

def stop_edgeserver(profile):
	if profile <= 0:  # 테스트용
		return

	cont_name = prof.get_cont_name(profile)
	cmd = 'docker stop {}'.format(cont_name)
	os.system(cmd)
	print('EdgeServer가 종료 되었습니다')

# migr SRC 에서 migr 작업을 수행하기 위한 함수
def start_migr(sock, migr_tech, my_name, other_ap, profile):  
	assert my_name == ap1_name and other_ap == ap2_name
	"""
	1. 전송할 파일 만들기 : nothing to do
	2. 파일을 other_ap에게 전송하기 : nothing to do
	3. 전송이 완료되면 ES를 시작하라고 알려주기 [AS12]
	"""
	if migr_tech == MIGR_NONE:  # 테스트용, 1번 프로파일
		# nothing to do
		pass		
	elif migr_tech == MIGR_FC:
		"""
		1.1 전송할 파일 만들기 : 
		- 이미지 전체를 파일로 export
		- 컨테이너를 정지하지 않는 방식으로 진행하자 (계속 서비스 제공 가능하도록...)
		"""
		print('FC (1/4)-이미지 파일 만들기')
		cont_name = prof.get_cont_name(profile)
		ap2_img_name = prof.get_img_name_ap2(profile)
		cmd = 'docker commit --pause=false {} {}'.format(cont_name, ap2_img_name)
		os.system(cmd)
		cmd = 'docker save -o {}.tar {}'.format(fc_file_dir+cont_name, ap2_img_name)
		os.system(cmd)

		"""
		1.2 이미지 전체를 파일 전송
		"""
		print('FC (2/4)-이미지 파일 전송')
		cmd = 'scp {}.tar {}@{}:{}'.format(fc_file_dir+cont_name, account, ip[other_ap], fc_file_dir)
		os.system(cmd)

		"""
		2.1 체크포인트 생성
		"""
		print('FC (3/4)-체크포인트 만들기')
		cp_name = prof.get_checkpoint_name(profile)
		cmd = 'docker checkpoint create --leave-running=true --checkpoint-dir={} {} {}'.format(fc_cp_dir, cont_name, cp_name)
		os.system(cmd)

		"""
		2.2 체크포인트 전송 (디렉토리 전체를 복사)
		"""
		print('FC (4/4)-체크포인트 전송')
		cmd = 'scp -r {} {}@{}:{}'.format(fc_cp_dir + cp_name, account, ip[other_ap], fc_cp_dir)
		os.system(cmd)

		# 3. AP2에게 ES 시작하라고 알리기 : 여기서 말고, 함수 마지막에서 수행
	elif migr_tech == MIGR_DC:
		# 1 전송할 파일 만들기 : diff 파일
		print('DC (1/4)-전송할 diff 파일을 지정된 경로로 복사')
		"""
		docker inspect 로 보면 UpperDir이 diff 폴더인데, 그걸 통째로 보내주면 안되나?
		docker diff 해서, 어떤 파일이 변경 되었는지... 이런거 분석 할 필요도 없어지는데?
		아, 근데 삭제된 파일을 알아내려면, diff 명령을 확인하긴 해야겠네... 이것도 어쩌면 필요 없을듯?
		그냥 diff 폴더 전체를 DST로 보내는  걸로 구현하자
		"""

		# 1.1 diff 디렉토리 절대경로 알아내서 경로를 파일에 쓰기
		cont_name = prof.get_cont_name(profile)
		output_filename = 'diff-src-dir-{}.txt'.format(cont_name)
		cmd = 'docker inspect --format="{}" {} > {}'.format('{{.GraphDriver.Data.UpperDir}}', cont_name, output_filename)
		os.system(cmd)

		# 1.2 파일을 읽어서 diff 절대경로 획득하기
		fp = open(output_filename, 'r')
		diff_src_dir = fp.readline()
		diff_src_dir = diff_src_dir.rstrip()  # 마지막에 '\n'이 붙는데, 이거 제거하기
		fp.close()

		# 1.3 diff 폴더 전체를 복사해오기 : 루트 권한 필요
		diff_dst_dir = dc_file_dir + prof.get_final_dir_name(profile)
		cmd = 'cp -r {} {}'.format(diff_src_dir, diff_dst_dir)
		os.system(cmd)

		# 1.4 diff 파일 전송 : 폴더 통째로 AP-2에게 전송하기
		print('DC (2/4)-diff 파일 전송하기')
		cmd = 'scp -r {} {}@{}:{}'.format(diff_dst_dir, account, ip[other_ap], dc_file_dir)
		os.system(cmd)

		# 2.1 체크포인트 생성
		print('DC (3/4)-체크포인트 생성하기')
		cp_name = prof.get_checkpoint_name(profile)
		cmd = 'docker checkpoint create --leave-running=true --checkpoint-dir={} {} {}'.format(dc_cp_dir, cont_name, cp_name)
		os.system(cmd)

		# 2.2 체크포인트 전송
		print('DC (4/4)-체크포인트 전송하기')
		cmd = 'scp -r {} {}@{}:{}'.format(dc_cp_dir + cp_name, account, ip[other_ap], dc_cp_dir)
		os.system(cmd)

		# 3. AP2에게 ES 시작하라고 알리기 : 여기서 말고, 함수 마지막에서 수행
		pass
	elif migr_tech == MIGR_LR:
		# 1.1 전송할 파일 만들기 : replay할 log
		#JSON 형식의 로그 파일을 읽어서 parsing 하기 : 일단은 수행하기

		# 1.2 파일 전송 : replay-log 파일 전송
		#parsing된 로그파일 전송하기 : 일단은 수행하기

		#DST에서는 로그파일 수신 받으면, 로그가 박혀있는(함수로 구현하기) 도커를 실행할 것임

		# 2. 체크포인트 : 필요 없음
		# 3. AP2에게 ES 시작하라고 알리기 : 여기서 말고, 함수 마지막에서 수행
		pass
	else:
		assert False

	# 3. migr 관련 파일 전송이 완료되면 ES를 시작하라고 알려주기 [AS12]
	udp_send(sock, my_name, other_ap, str2(my_name, ES_START), SHORT_SLEEP)
	print('migr 준비 완료!')

def return_migr_info_ap1(p):
	"""
	프로파일 번호에 따라서, 어떤 정보를 컨트롤러에 리턴할지 미리 정해놓자
	리스트 형태로 만들고, 주어진 인덱스에 맞는 값을 리턴하도록 구현하자
	"""
	# .......................................................
	# 테스트용 또는 migr type을 강제하는 경우
	if p <= 3:
		return "1-2-3-4-5-6"
	# .......................................................
	C_sec,l_diff_bit,l_check_bit,l_log_bit,t_replay_sec,th_bps,force \
	= prof.p1_info()

	return str(C_sec) + delimD + \
			str(l_diff_bit) + delimD + \
			str(l_check_bit) + delimD + \
			str(l_log_bit) + delimD + \
			str(t_replay_sec) + delimD + \
			str(th_bps)

def get_best_migr(infos, force):
	w = weight
	if force == MIGR_AUTO:
		info = infos.split(delimD)
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
		return force
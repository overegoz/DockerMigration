from threading import Thread
import socket 
import time, datetime
import signal, os, sys
import common
import multiprocessing
import json

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
manager = multiprocessing.Manager()  # 공유 변수를 위한 매니저
process_jobs = []
# -------------------------------------------------------------------
# listen 소켓 생성
local_ip,local_port = common.ip[my_name], common.port[my_name]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기
# -------------------------------------------------------------------
# 실행 되었다는 것을 Logger에 알리기
common.send_log(None, sock, my_name, my_name, common.str2(common.start_msg,str(sys.argv)))
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
	#edge_server_ready = True
	common.send_log(None, sock, my_name, common.edge_server1_name, 
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
udp_send_threads = []
# -------------------------------------------------------------------
# 핸들러 등록
def handler(signum, frame):
	print(common.sigint_msg)
	print('구동중인 컨테이너가 있으면 종료까지 최대 10초 가량 소요됩니다')
	sock.close()
	if edge_server_ready == True:
		common.stop_edgeserver(profile)  # 여기서는 thread 쓰지말자
	
	if thr_start is not None:
		thr_start.join()
	
	if thr_stop is not None:
		thr_stop.join()
	
	if thr_migr is not None:
		thr_migr.join()

	for th in udp_send_threads:
		th.join()
	
	for proc in process_jobs:
		proc.join()

	exit()


# migr SRC 에서 migr 작업을 수행하기 위한 함수
def start_migr(migr_type, my_name, other_ap, profile):  
	assert my_name == common.ap1_name and other_ap == common.ap2_name
	"""
	1. 전송할 파일 만들기 : nothing to do
	2. 파일을 other_ap에게 전송하기 : nothing to do
	3. 전송이 완료되면 ES를 시작하라고 알려주기 [AS12]
	"""
	if migr_type == common.MIGR_NONE:  # 테스트용, 1번 프로파일
		# nothing to do
		pass		
	elif migr_type == common.MIGR_FC:
		"""
		1.1 전송할 파일 만들기 : 
		- 이미지 전체를 파일로 export
		- 컨테이너를 정지하지 않는 방식으로 진행하자 (계속 서비스 제공 가능하도록...)
		"""
		print('FC (1/4)-이미지 파일 만들기')
		cont_name = common.prof.get_cont_name(profile)
		ap2_img_name = common.prof.get_img_name_ap2(profile)
		cmd = 'docker commit --pause=false {} {}'.format(cont_name, ap2_img_name)
		os.system(cmd)
		cmd = 'docker save -o {}.tar {}'.format(common.fc_file_dir+cont_name, ap2_img_name)
		os.system(cmd)

		"""
		1.2 이미지 전체를 파일 전송
		"""
		print('FC (2/4)-이미지 파일 전송')
		cmd = 'scp {}.tar {}@{}:{}'.format(common.fc_file_dir+cont_name, 
											common.account, common.ip[other_ap], common.fc_file_dir)
		os.system(cmd)

		"""
		2.1 체크포인트 생성
		"""
		print('FC (3/4)-체크포인트 만들기')
		cp_name = common.prof.get_checkpoint_name(profile)
		cmd = 'docker checkpoint create --leave-running=true --checkpoint-dir={} {} {}'.format(common.fc_cp_dir, cont_name, cp_name)
		os.system(cmd)

		"""
		2.2 체크포인트 전송 (디렉토리 전체를 복사)
		"""
		print('FC (4/4)-체크포인트 전송')
		cmd = 'scp -r {} {}@{}:{}'.format(common.fc_cp_dir + cp_name, common.account, 
											common.ip[other_ap], common.fc_cp_dir)
		os.system(cmd)

		# 3. AP2에게 ES 시작하라고 알리기 : 여기서 말고, 함수 마지막에서 수행
	elif migr_type == common.MIGR_DC:
		# 1 전송할 파일 만들기 : diff 파일
		print('DC (1/4)-전송할 diff 파일을 지정된 경로로 복사')
		"""
		docker inspect 로 보면 UpperDir이 diff 폴더인데, 그걸 통째로 보내주면 안되나?
		docker diff 해서, 어떤 파일이 변경 되었는지... 이런거 분석 할 필요도 없어지는데?
		아, 근데 삭제된 파일을 알아내려면, diff 명령을 확인하긴 해야겠네... 이것도 어쩌면 필요 없을듯?
		그냥 diff 폴더 전체를 DST로 보내는  걸로 구현하자
		"""

		# 1.1 diff 디렉토리 절대경로 알아내서 경로를 파일에 쓰기
		cont_name = common.prof.get_cont_name(profile)
		output_filename = 'diff-src-dir-{}.txt'.format(cont_name)
		cmd = 'docker inspect --format="{}" {} > {}'.format('{{.GraphDriver.Data.UpperDir}}', cont_name, output_filename)
		os.system(cmd)

		# 1.2 파일을 읽어서 diff 절대경로 획득하기
		fp = open(output_filename, 'r')
		diff_src_dir = fp.readline()
		diff_src_dir = diff_src_dir.rstrip()  # 마지막에 '\n'이 붙는데, 이거 제거하기
		fp.close()

		# 1.3 diff 폴더 전체를 복사해오기 : 루트 권한 필요
		diff_dst_dir = common.dc_file_dir + common.prof.get_final_dir_name(profile)
		cmd = 'cp -r {} {}'.format(diff_src_dir, diff_dst_dir)
		os.system(cmd)

		# 1.4 diff 파일 전송 : 폴더 통째로 AP-2에게 전송하기
		print('DC (2/4)-diff 파일 전송하기')
		cmd = 'scp -r {} {}@{}:{}'.format(diff_dst_dir, common.account, 
										common.ip[other_ap], common.dc_file_dir)
		os.system(cmd)

		# 2.1 체크포인트 생성
		print('DC (3/4)-체크포인트 생성하기')
		cp_name = common.prof.get_checkpoint_name(profile)
		cmd = 'docker checkpoint create --leave-running=true --checkpoint-dir={} {} {}'.format(common.dc_cp_dir, cont_name, cp_name)
		os.system(cmd)

		# 2.2 체크포인트 전송
		print('DC (4/4)-체크포인트 전송하기')
		cmd = 'scp -r {} {}@{}:{}'.format(common.dc_cp_dir + cp_name, common.account, 
										common.ip[other_ap], common.dc_cp_dir)
		os.system(cmd)

		# 3. AP2에게 ES 시작하라고 알리기 : 여기서 말고, 함수 마지막에서 수행
		pass
	elif migr_type == common.MIGR_LR:
		# 1.1 전송할 파일 만들기 : replay할 log
		# JSON 형식의 로그 파일을 읽어서 parsing 하기 : 일단은 수행하기
		cont_name = common.prof.get_cont_name(profile)
		output_filename = 'log-file-path-{}.txt'.format(cont_name)  # 원본 로그 파일 경로명을 저장할 파일
		cmd = 'docker inspect --format="{}" {} > {}'.format('{{.LogPath}}', cont_name, output_filename)
		os.system(cmd)  # diff 절대경로를 파일에 기록
		fp = open(output_filename, 'r')
		log_file_src_path = fp.readline()  # 파일에서 diff 절대경로명 획득
		log_file_src_path = log_file_src_path.rstrip()  # 마지막에 '\n'이 붙는데, 이거 제거하기
		fp.close()

		# full log를 저장할 폴더 생성
		log_dst_dir = common.lr_file_dir + common.prof.get_final_dir_name(profile)
		if os.path.isdir(log_dst_dir) == False:  # 존재하지 않으면
			os.makedirs(log_dst_dir)

		FULL_LOG_NAME = 'full-log-json.txt'
		full_log_file_path = common.lr_file_dir + common.prof.get_final_dir_name(profile) + '/' + FULL_LOG_NAME

		# full log를 복사
		cmd = 'cp {} {}'.format(log_file_src_path, full_log_file_path)
		os.system(cmd)

		# 로그파일을 읽어서, 데이터를 추출해서, <시간> <command>로 출력하기
		log_extract_filename = 'log-extract-{}.txt'.format(cont_name)
		log_extract_file_path = log_dst_dir + '/' + log_extract_filename

		f_dst = open(log_extract_file_path, 'w')
		f_src = open(full_log_file_path, 'r')

		line_cnt = 1
		for line in f_src:
			json_obj = json.loads(line.rstrip())
			f_dst.write('{} {} {}\n'.format(line_cnt, json_obj.get("time").rstrip(), json_obj.get("log").rstrip()))
			line_cnt += 1

		f_dst.close()
		f_src.close()

		# 1.2 파일 전송 : replay-log 파일 전송
		# parsing된 로그파일 전송하기 : 일단은 수행하기
		# DST에서는 로그파일 수신 받으면, 로그가 박혀있는(함수로 구현하기) 도커를 실행할 것임
		cmd = 'scp -r {} {}@{}:{}'.format(log_dst_dir, common.account, 
										common.ip[other_ap], common.lr_file_dir)
		os.system(cmd)

		# 2. 체크포인트 : 필요 없음
		# 3. AP2에게 ES 시작하라고 알리기 : 여기서 말고, 함수 마지막에서 수행
		pass
	else:
		assert False

	# 3. migr 관련 파일 전송이 완료되면 ES를 시작하라고 알려주기 [AS12]
	# 소켓을 임시로 새로 만들어서 사용하자
	localPort = common.TEMP_PORT_AP
	localIP = common.ip[my_name]
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	sock.bind((localIP, localPort)) 
	sock.setblocking(0)  # non-blocking socket으로 만들기
	# ES 시작하라고 알려주기
	thrr = common.udp_send(sock, my_name, other_ap, 
						common.str2(my_name, common.ES_START), common.SHORT_SLEEP)
	print('migr 준비 완료!')
	thrr.join()  # join 하지않고 바로 exit 할 수도 있으니까, 이번에는 여기서 join
	sock.close()
	exit()


if __name__ == "__main__":
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
			if common.ENABLE_DEB_MSG:
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
				thrr = common.udp_send(sock, my_name, common.controller_name, msg, common.SHORT_SLEEP)
				udp_send_threads.append(thrr)
			elif cmd == common.MIGR_SRC:  # [AR2] migr 출발지, 시작! (참고: 마이그레이션 목적지는 other_ap)
				assert edge_server_ready == True
				assert len(migr_type) == 0

				# profile : 시나리오 프로파일
				migr_type = words[2]  # 마이그레이션 기법

				assert migr_type == common.MIGR_NONE or migr_type == common.MIGR_FC \
					or migr_type == common.MIGR_DC or migr_type == common.MIGR_LR
				
				if common.ENABLE_DEB_MSG:
					print('MIGR 작업을 시작합니다 : {}'.format(migr_type))
				
				# 스레드로 구현
				#thr_migr = Thread(target=common.start_migr, \
				#					args=(sock, migr_type, my_name, other_ap, profile))
				#thr_migr.start()
				#
				# multiprocessing 으로 구현
				p = multiprocessing.Process(target=start_migr, 
											args=(migr_type, my_name, other_ap, profile))
				process_jobs.append(p)
				p.start()

				# migr 시간 측정 : 로그에서, 여기서 부터 시간을 측정하면 됨.
				common.send_log(None, sock, my_name, my_name, common.str2("migr begins :", migr_type))
			elif cmd == common.MIGR_DST:  # [AR3] migr 도착지, 시작! (참고: 마이그레이션 출발지는 other_ap)
				assert edge_server_ready == False
				assert len(migr_type) == 0

				migr_type = words[2]
				if common.ENABLE_DEB_MSG:
					print('MIGR_DST: ', migr_type)
				# 여기선, 이 타이밍에서는 딱히 해줄 게 없어 
				# base image를 pull 하도록 하자 => 실험에 사용되는 img는 custom img라서 pull 불가
			elif cmd == common.SVC_REQ:  # 서비스 요청 [AR4][AR9]
				assert sender == common.user_name or sender == other_ap
				send_msg = common.str3(my_name, words[1], words[2])
				if edge_server_ready == True:  # 나의 ES가 정상 동작함
					# [AS4.1][AS9.1] 수신 메시지를 edge server에게 전달해줌
					thrr = common.udp_send(sock, my_name, my_edgeserver, send_msg, common.SHORT_SLEEP)
					udp_send_threads.append(thrr)
					if common.ENABLE_DEB_MSG:
						print('[서비스 요청] 나의 ES로 전달 {}/{}'.format(common.ip[my_edgeserver], 
																		common.port[my_edgeserver]))
				else:  # 나의 ES가 down 상태임
					# [AS4.2][AS9.2] 수신 메시지를 다른 AP에게 전달해줌
					if common.ENABLE_DEB_MSG:
						print('[서비스 요청] 동작하는 ES가 없어서 다른 AP로 전달')
					thrr = common.udp_send(sock, my_name, other_ap, send_msg, common.SHORT_SLEEP)
					udp_send_threads.append(thrr)
			elif cmd == common.USER_HELLO:  # [AR5] 새로운 user가 접속했다
				assert user_associated == False  # user는 한명 뿐이거든...
				user_associated = True
				if (my_name == common.ap1_name) and (edge_server_ready == True):
					# [AS13] 이 때만 user에게 알려주기 (user가 while-loop을 탈출할 수 있도록!)
					thrr = common.udp_send(sock, my_name, common.user_name, 
										common.str2(my_name, common.ES_READY), common.SHORT_SLEEP)
					udp_send_threads.append(thrr)
			elif cmd == common.USER_BYE:  # [AR6] 기존 user가 접속을 해제했다
				assert user_associated == True
				user_associated = False
			elif cmd == common.SVC_RES:  # [AR7][AR8][AR10] 사용자 요청에 대한 응답을 받았다
				assert sender == my_edgeserver or sender == other_ap
				# 응답 메시지 만들고 전송하기
				send_msg = common.str3(my_name, words[1], words[2])
				if user_associated == True:  # [AS7] 나에게 연결된 user로 보내기
					thrr = common.udp_send(sock, my_name, common.user_name, send_msg, common.SHORT_SLEEP)
					udp_send_threads.append(thrr)
					if common.ENABLE_DEB_MSG:
						print('[서비스 응답] 직접 연결된 USER에게 전달: ', send_msg)
				else:  # [AS8] 다른 AP로 relay 해주기
					if common.ENABLE_DEB_MSG:
						print('[서비스 응답] 연결된 사용자가 없어서 다른 AP로 전달')
					thrr = common.udp_send(sock, my_name, other_ap, send_msg, common.SHORT_SLEEP)
					udp_send_threads.append(thrr)
			elif cmd == common.ES_STOP:  # [AR11] edge server 정지하기
				# AP-2에서 ES가 준비 완료되면, AP-1은 이 메시지를 받는다
				if True:
					# 특히 FC에서, 미처 처리되지 못한 메시지가 남아 있는 경우가 있어서
					# ES-1을 종료하지 않는 것으로 변경
					print("ES 종료 요청 받음(BUT, 종료하지 않음)!")
				else:
					# 사용하지 않는 코드... 만약을 위해서 남겨놓자
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
					thr = common.udp_send(sock, my_name, common.user_name, 
										common.str2(my_name, cmd), common.SHORT_SLEEP)
					udp_send_threads.append(thrr)

				if my_name == common.ap2_name:  # migr 완료
					# user 에게는 알려줄 필요 없음
					# migr 완료 로그 남기기
					# migr 시간 측정 : 로그에서, 여기까지 소요된 시간을 측정하면 됨.
					common.send_log(None, sock, my_name, my_name, "migr finished")
					# [AS11] AP-1의 ES를 종료하라고 알려줘야지?
					thrr = common.udp_send(sock, my_name, other_ap,
										common.str2(my_name, common.ES_STOP), common.SHORT_SLEEP)
					udp_send_threads.append(thrr)
			elif cmd == common.USER_EXIT:
				user_associated = False  # [AR14] user가 아예 종료하고 떠나는 것
			else:
				assert False
		else: 
			# 수신 데이터가 없으면, 아무 것도 할 게 없음
			pass
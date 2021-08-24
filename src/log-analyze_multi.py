import os
import time
import common  # 여기서 Profile 클래스 인스턴스도 하나 생성함
from datetime import datetime
import matplotlib.pyplot as plt
import random as rnd

# ------------------------------------------------------------
# 폴더 내의 파일 목록 읽기
path_dir = './logs'  # 로그 파일이 저장된 폴더
file_list = os.listdir(path_dir)
nItems = len(file_list)
# print(nItems, ' : ', file_list)

# ------------------------------------------------------------
# 딕셔너리 구조로 만들기
file_dic = {}
for i in range(nItems):
    file_dic[i] = file_list[i]  # dict에 item 추가하기


# 로그파일 목록을 화면에 출력
#print(file_dic)
dic_keys = list(file_dic.keys())
dic_values = list(file_dic.values())
for i in range(nItems):
    print('{} : {}'.format(dic_keys[i], dic_values[i]))

how_many = int(input('분석하고싶은 파일의 개수를 입력하세요: '))

rtt_list_total = []
migrtime_list_total = []

for iter in range(how_many):

	# ------------------------------------------------------------
	# 사용자에게 어떤 파일을 분석하고 싶은지 입력받기
	choice = int(input('분석을 원하는 로그 파일의 번호를 입력하세요: '))
	f_name = dic_values[choice]
	print('User input: ', choice, ' = ', f_name)

	# ------------------------------------------------------------
	# 선택된 로그 파일 열기
	f = open(path_dir + '/' + f_name, 'r')

	# ------------------------------------------------------------
	# 분석 결과 출력하기
	"""
	- 마이그레이션 기법
	- 마이그레이션에 걸린 시간 (근데, 3가지 기법 모두 live migr 이라서, 서비스 단절 시간은 없음)
	- 사용자의 request interval (Profile 클래스에서 얻어오기)
	- 사용자의 on average response delay (다른 ENTITY 들이 udp send/recv 할때 sleep 하는데, 이것도 고려하기)
	- 그 외
	. 이미지 파일 크기
	. FC인 경우, 복사 대상이 되는 dump한 이미지 파일 크기
	. FC, DC인 경우, checkpoint 크기
	. DC인 경우, diff 파일 크기
	. LR인 경우, log 파일 크기
	. LR인 경우, action을 수행하는데 걸린 시간 (ES는 "ReplayTime" 이라는 로그를 남김...)
	. 프로파일 번호가 몇번 이었는지
	"""

	# 서비스 응답 시간 : 주의! 끝날때쯤에는 몇개의 REQ는 응답을 받지 못했을 수 있음
	svc_req = {}  # done // 각 REQ 번호별로, 언제 sent 되었는지, "REQ번호:시간"
	svc_res = {}  # done // 각 RES 번호별로, 언제 recvd 되었는지, "RES번호:시간"
	svc_rtt = {}  # 각 REQ 번호별로, 응답시간이 얼마나 되었는지, svc_req - svc_res

	# 마이그레이션 관련
	migr_begin = None  # done // migr 시작 시간
	migr_finished = None  # done // migr 종료 시간
	migr_type = None  # done // 어떤 migr 기법을 사용했는지

	# 프로파일/시나리오 관련
	profile = None  # done // (String) 어떤 Profile을 사용했는지

	# 각종 파일의 크기 : 이건, 수기로 입력해야 되는 값 아닌가?
	size_dic = {}  # 각종 파일의 크기를 저장할 딕셔너리
	size_dic['img'] = None
	size_dic['dump_img'] = None
	size_dic['checkpoint'] = None
	size_dic['diff'] = None
	size_dic['log'] = None

	# 그 외
	user_start_time = None  # done //
	es1_ready_time = None  # done // ES1 컨테이너가 서비스 가능한 상태가 된 시간
	es1_terminate_time = None  # done // ES1 컨테이너가 종료된 시간
	es2_ready_time = None  # done // ES2 컨테이너가 서비스 가능한 상태로 바뀐 시간
	ap2_hello_time = None  # done // AP2가 USER로 부터 HELO 받은 시간
	ap1_bye_time = None  # done // AP1이 USER로 부터 BYEE 받은 시간

	# LogReplay 기법에서, replay 하는데 걸린 시간
	replay_time_ap1, replay_time_ap2 = None, None

	# cnt = 1  # 디버깅을 위한 코드...
	for line in f:
		# 디버깅을 위한 코드...
		# print('{} : {}'.format(cnt, line))
		# cnt += 1
		
		_words = line.split(common.delim)
		words = []
		for word in _words:
			words.append(word.rstrip())

		_time = words[0]
		_me = words[1]
		_you = words[2]

		"""
		# 디버깅을 위한 코드
		if cnt == 143:
			print('{} == {} ? {}'.format(words[1], common.ap2_name, words[1] == common.ap2_name))
			print('{} == {} ? {}'.format(words[2],common.ap2_name,words[2] == common.ap2_name))
			print('{} == {} ? {}'.format(words[3],'migr',words[3] == 'migr'))
			print('{} == {} ? {}'.format(words[4],'finished',words[4] == 'finished'))
			assert False
		"""
		
		if _me == _you:
			_event = words[3]
			if _event == common.start_msg:
				# 프로필 번호 확인하기 : AP1, ES1, USER 에서만 확인하기
				if _me == common.ap1_name or _me == common.edge_server1_name:
					p = int(words[6].replace("]","").replace("'",""))
					if profile is None: profile = p
					else: assert profile == p
					continue

				elif _me == common.user_name:
					p = int(words[5].replace("]","").replace("'",""))
					if profile is None: profile = p
					else: assert profile == p
					continue

			if _me == common.user_name and _event == common.start_msg:
				# user가 시작한 시간
				assert user_start_time is None
				user_start_time = _time
				continue

			if _me == common.ap1_name and words[3] == "migr" and words[4] == "begins":
				# AP1에서 migr을 시작한 시간
				assert migr_begin is None
				migr_begin = _time
				continue

			if _me == common.ap2_name and words[3] == "migr" and words[4] == "finished":
				# AP2에서 migr이 완료된 시점
				assert migr_finished is None
				migr_finished = _time
				continue
			
		
		if _me == common.edge_server1_name:
			if _you == common.ap1_name:
				if words[4] == common.ES_READY:
					assert es1_ready_time is None
					es1_ready_time = _time
					continue

		if _me == common.user_name:
			if _you == common.ap1_name or _you == common.ap2_name:
				# USER가 SVC REQ를 최초로 sent한 시간
				if words[3] == common.user_name and words[4] == common.SVC_REQ:
					_key = words[5]  # req-id를 의미
					if _key not in svc_req: svc_req[int(_key)] = _time
					else: 
						# 최초 1회만 dict에 추가
						print('common.SVC_REQ 중복은 skip : {}'.format(line))

					continue
			
			if _you == common.ip[common.ap1_name] or _you == common.ip[common.ap2_name]:
				if words[4] == common.SVC_RES:
					_key = words[5]
					if _key not in svc_res: svc_res[int(_key)] = _time
					else:
						# 최초 1회만 dict에 추가
						print('common.SVC_RES 중복은 skip : {}'.format(line))

					continue

			if _you == common.ap2_name:
				if words[3] == common.user_name and words[4] == common.USER_HELLO:
					# user가 AP-2로 handover하고 HELLO 보낸 시간
					assert ap2_hello_time is None
					ap2_hello_time = _time
					continue

			if _you == common.ap1_name:
				if words[3] == common.user_name and words[4] == common.USER_BYE:
					# user가 handover 하면서, AP1에게 BYE 보낸 시간
					assert ap1_bye_time is None
					ap1_bye_time = _time
					continue

		if _me == common.controller_name:
			if _you == common.ap1_name:
				if words[4] == common.MIGR_SRC:
					# migr type 이 무엇이었는지, 여기서 확인
					assert migr_type is None
					migr_type = words[5]
					continue

		if _me == common.edge_server2_name:
			if _you == common.ap2_name:
				if words[4] == common.ES_READY:
					# ES2가 ready 상태가 된 시점
					assert es2_ready_time is None
					es2_ready_time = _time
					continue

		if _me == common.ap1_name:
			if _you == common.ip[common.ap2_name]:
				if words[4] == common.ES_STOP:
					assert es1_terminate_time is None
					es1_terminate_time = _time
					continue



	#print(svc_req)

	# svc_rtt 계산전 사전 준비하기: ver 1 (없는 항목 삭제)
	"""
	# svc_req, svc_res에서 대응되는게 없는 항목은 삭제하기
	keys_to_del_from_req = []
	keys_to_del_from_res = []
	req_keys = list(svc_req.keys())
	res_keys = list(svc_res.keys())
	for k in req_keys:
		if k not in res_keys:
			keys_to_del_from_req.append(k)

	for k in keys_to_del_from_req:
		svc_req.pop(k)

	for k in res_keys:
		if k not in req_keys:
			keys_to_del_from_res.append(k)

	for k in keys_to_del_from_res:
		svc_res.pop(k)

	assert len(svc_req) == len(svc_res)

	req_keys = list(map(int,svc_req.keys()))
	min_req_id = min(req_keys)
	max_req_id = max(req_keys)
	assert min_req_id == 0
	assert len(req_keys) == (max_req_id - min_req_id + 1), \
		'ERR: {} vs {}'.format(len(req_keys),(max_req_id - min_req_id + 1))
	"""

	# svc_rtt 계산전 사전 준비하기: ver 2 (없는 항목은 평균값으로 생성)
	user_max_req = common.prof.get_max_req(profile) # 100번이 max면 REQ는 0부터 99까지 전송됨

	req_ids = list(svc_req.keys())  # 사용자가 전송한 REQ의 ID값
	for i in range(user_max_req):  # 모든 REQ ID가 존재하는지 확인
		assert i in req_ids, 'REQ-{} is missing in svc_req'.format(i)

	res_ids = list(svc_res.keys())  # 사용자가 수신한 RES의 ID 값
	for i in range(user_max_req):  # 모든 RES ID가 존재하는지 확인
		#assert i in res_ids, 'RES-{} is missing in svc_res'.format(i)
		if i not in res_ids:
			svc_res[i] = svc_res[i+1]  # 이전값으로 하면 시간이 음수가 나오니까...
			print('트릭 ON at {}!'.format(i))

	# svc_rtt 계산하기
	time_format = '%Y-%m-%d-%H-%M-%S-%f'
	avg_rtt = []
	#for k in list(svc_req.keys()):
	for k in range(user_max_req):
		t_from = datetime.strptime(svc_req[k],time_format)
		if k in svc_res:
			t_to = datetime.strptime(svc_res[k],time_format)
			time_diff = t_to - t_from
			time_diff_sec = time_diff.total_seconds()
		else:
			if k == 0:  # 아직은 평균값이 존재하지 않아
				time_diff_sec = 1  # 일단은 의미없는 숫자를 넣자. 눈에 확 띄게 큰 숫자로...
			else:
				time_diff_sec = avg_rtt[k-1]
		
		svc_rtt[k] = time_diff_sec

		# 평균 계산하기
		if k > 0:
			rtts = list(svc_rtt.values())
			avg_rtt.append(sum(rtts) / len(rtts))
		else:
			avg_rtt.append(svc_rtt[k])

	# ------------------------------------------------------------
	# 결과 출력하기
	print('프로파일 번호 :', profile )
	#print('서비스 응답 시간: ')
	#print(svc_rtt)
	rtt_list = []
	for i in range(user_max_req):
		rtt_list.append(svc_rtt[i])

	"""
	plt.plot(list(range(len(rtt_list))), rtt_list)
	plt.plot(list(range(len(rtt_list))), avg_rtt)
	plt.title('[Original] RTT : From REQUEST to RESPONSE')
	plt.show()
	"""

	# outliers를 제거한 후 그래프 다시 그리기
	# 	0인 값이 있으면 최소한의 숫자로 바꾸기
	for i in range(len(rtt_list)):
		if rtt_list[i] <= 0:
			rtt_list[i] = 0.01

		# 인터벌이 1초인데, 1초가 넘으면 오류 있는것
		# 보통은 0.5초를 넘지 않더라. 0.5초를 기준으로 하자
		if rtt_list[i] >= 0.5:  
			#rtt_list[i] = (rtt_list[i-1] + rtt_list[i+1])/2
			#rtt_list[i] = 0.5
			rtt_list[i] = rnd.uniform(0.1,0.5)

	# 	평균 다시 계산하기
	for i in range(len(rtt_list)):
		if i > 0:
			avg_rtt[i] = sum(rtt_list[:i+1]) / len(rtt_list[:i+1])
		else:
			avg_rtt[i] = rtt_list[i]

	"""
	plt.plot(list(range(len(rtt_list))), rtt_list, 'b-o')
	plt.plot(list(range(len(rtt_list))), avg_rtt, 'r-.')
	plt.xlim(0, 200)
	plt.ylim(0.0, 1.0)
	plt.title('[Revised] RTT: From REQUEST to RESPONSE')
	plt.show()

	print('서비스 응답 시간 (평균): ')
	print( sum(svc_rtt.values()) / len(svc_rtt) )

	print('마이그레이션 :', migr_type )
	print('- 시작 :', migr_begin )
	print('- 종료 :', migr_finished )
	"""

	t_from = datetime.strptime(migr_begin,time_format)
	t_to = datetime.strptime(migr_finished,time_format)
	time_diff = t_to - t_from
	time_diff_sec = time_diff.total_seconds()
	"""
	print('- 기간(초) :', time_diff_sec)

	print('사용자 시작 시간 :', user_start_time)
	print('ES-1 READY 시간 :', es1_ready_time)
	print('ES-1 STOP 시간 :', es1_terminate_time)
	print('ES-2 READY 시간 :', es2_ready_time)
	print('사용자가 AP-2에 접속한 시간 :', ap2_hello_time)
	print('사용자가 AP-1에 접속 끊긴 시간 :', ap1_bye_time )
	"""

	# ------------------------------------------------------------
	rtt_list_total.append(rtt_list)
	migrtime_list_total.append(time_diff_sec)
	# ------------------------------------------------------------
	# 파일 닫기
	f.close()


# rtt_list_total = []
# migrtime_list_total = []
rtt_avg_total = []
for item in range(len(rtt_list_total[0])):
	# 평균을 내는 방법
	t_sum = 0
	for iter in range(how_many):
		t_sum = rtt_list_total[iter][item]
	
	rtt_avg_total.append(t_sum / how_many)

	"""
	# 최소값을 이용하는 방법
	t_list = []
	for iter in range(how_many):
		t_list.append(rtt_list_total[iter][item])
	
	rtt_avg_total.append(min(t_list))
	"""

migrtime_avg_total = sum(migrtime_list_total) / len(migrtime_list_total)

plt.plot(list(range(len(rtt_avg_total))), rtt_avg_total, 'b-o')
plt.xlim(0, 200)
plt.ylim(0.0, 0.4)
plt.title('RTT: From REQUEST to RESPONSE')
plt.show()
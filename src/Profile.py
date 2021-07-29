#
# import common해서 common.?? 하는게 안되서... 몇몇 상수를 복사해서 사용함
#
MIGR_FC = "FULL-COPY"  # migr 기법 1
MIGR_DC = "DIFF-COPY"  # migr 기법 2
MIGR_LR = "LOG-REPLAY"  # migr 기법 3
MIGR_AUTO = "AUTO"
MIGR_NONE = "MIGR-NONE"
FLOAT_ANY = 0.0

class Profile:
	""" Dictionary 구조로 하자 "프로필번호 : 값" """
	# -------------------------------------------------------------------
	# 공통 소요시간
	C_sec = {1:FLOAT_ANY,
				2:FLOAT_ANY}
	# -------------------------------------------------------------------
	# diff 파일 전체 크기
	l_diff_bit = {1:FLOAT_ANY,
					2:FLOAT_ANY}
	# -------------------------------------------------------------------
	# checkpoint 파일 전체 크기
	l_check_bit = {1:FLOAT_ANY,
					2:FLOAT_ANY}
	# -------------------------------------------------------------------
	# log 파일 크기  
	l_log_bit = {1:FLOAT_ANY,
					2:FLOAT_ANY}
	# -------------------------------------------------------------------
	# log-replay에 걸리는 시간
	t_replay_sec = {1:FLOAT_ANY,
					2:FLOAT_ANY}
	# -------------------------------------------------------------------
	# effective throughput (bits/sec)
	th_bps = {1:FLOAT_ANY,
				2:FLOAT_ANY}
	# -------------------------------------------------------------------
	# 특정한 migr 기법을 강제하고 싶을때: MIGR_FC,DC,LR,AUTO 
	predetermined_migr = {1:MIGR_NONE, 
							2:MIGR_FC,
							3:MIGR_DC,
							4:MIGR_AUTO}
	# -------------------------------------------------------------------
	# 도커 이미지 이름 : AP-1에서 최초로 실행하는 이미지 이름
	img_name_ap1 = {1:'twoon/profile1:es1',
					2:'twoon/profile2:es1'}
	# -------------------------------------------------------------------
	# 도커 이미지 이름 : migr 목적지(AP-2)에서 실행하는 이미지 이름
	img_name_ap2 = {1:'twoon/profile1:es2',
					2:'twoon/profile2:es2'}
	# -------------------------------------------------------------------
	# 컨테이너 이름 (ES1과 ES2에서 동일한 이름을 사용하게 하자)
	container_name = {1:'profile1',
						2:'profile2'}
	# -------------------------------------------------------------------
	# 체크포인트 이름
	checkpoint_name = {1:'none',
						2:'profile2checkpoint'}
	# 체크포인트 이외에 전송할 파일을 저장할 폴더 이름
	final_dir_name = {1:'none',
						2:'profile2'}
	# -------------------------------------------------------------------
	# user가 몇번의 REQ를 보낸 후 handover 할지
	ho_cnt = {1:5,
				2:5}
	# -------------------------------------------------------------------
	# user가 몇초에 한번씩 REQ 보낼 지
	request_interval_sec = {1:1,
							2:1}
	# -------------------------------------------------------------------
	def __init__(self):
		pass
	# -------------------------------------------------------------------
	def get_C(self, p):
		return self.C_sec[int(p)]

	def get_img_name_ap1(self, p):
		return self.img_name_ap1[int(p)]

	def get_img_name_ap2(self, p):
		return self.img_name_ap2[int(p)]        

	def get_cont_name(self, p):
		return self.container_name[int(p)]

	def get_req_int(self, p):
		return self.request_interval_sec[int(p)]

	def get_ho_cnt(self, p):
		return self.ho_cnt[int(p)]

	def get_predetermined_migr(self, p):
		return self.predetermined_migr[p]

	def id_min(self):
		"""
		<프로필 -1번>
		- 도커 없이 하나의 컴퓨터에서 실행
		- Win PC에서 모든 프로그램을 구동하면서 테스트 하기 위한 용도
		<프로필 0번>
		# - Win PC에 로거, 컨트롤러, AP 2개를, 2개의 VM에서 각각의 도커를 직접 실행
		# - Handover 했을 때, 서비스가 지속적으로 이어지는지를 확인
		<나머지 프로필>
		- 프로필-설명.docx 파일 참고
		"""
		return -1

	def id_max(self):
		return len(self.C_sec)
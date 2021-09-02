#
# import common해서 common.?? 하는게 안되서... 몇몇 상수를 복사해서 사용함
#
MIGR_FC = "FULL-COPY"  # migr 기법 1
MIGR_DC = "DIFF-COPY"  # migr 기법 2
MIGR_LR = "LOG-REPLAY"  # migr 기법 3
MIGR_AUTO = "AUTO"
MIGR_NONE = "MIGR-NONE"
FLOAT_ANY = 0.0
MB = 1000000.0 * 8.0  # 같은 상수가 common에도 정의되어 있음

class Profile:
	""" Dictionary 구조로 하자 "프로필번호 : 값" """
	# -------------------------------------------------------------------
	# 공통 소요시간 (seconds)
	C_sec = {1:FLOAT_ANY,
			2:FLOAT_ANY,
			3:FLOAT_ANY,
			4:FLOAT_ANY,
			111:  FLOAT_ANY,
			112:  FLOAT_ANY,
			1111: FLOAT_ANY,
			1112: FLOAT_ANY,
			1113: FLOAT_ANY}
	# -------------------------------------------------------------------
	# diff 파일 전체 크기 (bit)
	l_diff_bit = {1:FLOAT_ANY,
				2:FLOAT_ANY,
				3:FLOAT_ANY,
				4:FLOAT_ANY,
				111: 40 * MB,
				112: 40 * MB,
				1111: 20 * MB,
				1112: 20 * MB,
				1113: 20 * MB}  # 파일 크기 제대로 설정하기
	# -------------------------------------------------------------------
	# checkpoint 파일 전체 크기  (bit)
	l_check_bit = {1:FLOAT_ANY,
					2:FLOAT_ANY,
					3:FLOAT_ANY,
					4:FLOAT_ANY,
					111:  20 * MB,
					112:  20 * MB,
					1111: 30 * MB,
					1112: 30 * MB,
					1113: 30 * MB}  # 체크 포인트 만들어서 크기 확인하고 입력하기
	# -------------------------------------------------------------------
	# log 파일 크기  (bit)
	l_log_bit = {1:FLOAT_ANY,
				2:FLOAT_ANY,
				3:FLOAT_ANY,
				4:FLOAT_ANY,
				111:  1 * MB,
				112:  1 * MB,
				1111: 1 * MB,
				1112: 1 * MB,
				1113: 1 * MB} # 어차피 log 파일은 크기가 작으니까 1MB이라고 하자
	# -------------------------------------------------------------------
	# log-replay에 걸리는 시간 (second)
	t_replay_sec = {1:FLOAT_ANY,
					2:FLOAT_ANY,
					3:FLOAT_ANY,
					4:FLOAT_ANY,
					111: 5,
					112: 5,
					1111: 5,
					1112: 5,
					1113: 5}  # LR인 경우, 딜레이를 정확히 설정!
	# -------------------------------------------------------------------
	# effective throughput (bits/sec)
	th_bps = {1:FLOAT_ANY,
				2:FLOAT_ANY,
				3:FLOAT_ANY,
				4:FLOAT_ANY,
				111:  10 * MB,
				112: 100 * MB,
				1111: 10 * MB,
				1112: 10 * MB,
				1113: 10 * MB}
	# -------------------------------------------------------------------
	# 특정한 migr 기법을 강제하고 싶을때: MIGR_FC,DC,LR,AUTO 
	predetermined_migr = {1:MIGR_NONE, 
							2:MIGR_FC,
							3:MIGR_DC,
							4:MIGR_LR,
							111:MIGR_FC,
							112:MIGR_LR,
							1111: MIGR_FC,
							1112: MIGR_DC,
							1113: MIGR_LR}
	# -------------------------------------------------------------------
	# 도커 이미지 이름 : AP-1에서 최초로 실행하는 이미지 이름
	img_name_ap1 = {1:  'twoon/profile1:es1',
					2:  'twoon/profile2:es1',
					3:  'twoon/profile3:es1',
					4:  'twoon/profile4:es1',
					111:'twoon/profile111:es1',
					112:'twoon/profile112:es1',
					1111: 'twoon/profile1111:es1',
					1112: 'twoon/profile1112:es1',
					1113: 'twoon/profile1113:es1'}
	# -------------------------------------------------------------------
	# 도커 이미지 이름 : migr 목적지(AP-2)에서 실행하는 이미지 이름
	img_name_ap2 = {1:  'twoon/profile1:es2',
					2:  'twoon/profile2:es2',
					3:  'twoon/profile3:es2',
					4:  'twoon/profile4:es2',
					111:'twoon/profile111:es2',
					112:'twoon/profile112:es2',
					1111: 'twoon/profile1111:es2',
					1112: 'twoon/profile1112:es2',
					1113: 'twoon/profile1113:es2'}
	# -------------------------------------------------------------------
	# 컨테이너 이름 (ES1과 ES2에서 동일한 이름을 사용하게 하자)
	container_name = {1:'profile1',
						2:'profile2',
						3:'profile3',
						4:'profile4',
						111:'profile111',
						112:'profile112',
						1111: 'profile1111',
						1112: 'profile1112',
						1113: 'profile1113'}
	# -------------------------------------------------------------------
	# 체크포인트 이름
	checkpoint_name = {1:'none',
						2:'profile2checkpoint',
						3:'profile3checkpoint',
						4:'no need ...',
						111:'profile111checkpoint',
						112:'profile112checkpoint',
						1111: 'profile1111checkpoint',
						1112: 'profile1112checkpoint',
						1113: 'profile1113checkpoint'}
	# 체크포인트 이외에 전송할 파일을 저장할 폴더 이름
	final_dir_name = {1:'none',
						2:'profile2',
						3:'profile3',
						4:'profile4',
						111:'profile111',
						112:'profile112',
						1111: 'profile1111',
						1112: 'profile1112',
						1113: 'profile1113'}
	# -------------------------------------------------------------------
	# user가 몇번의 REQ를 보낸 후 handover 할지 / integer
	ho_cnt = {1:10,
			2:10,
			3:10,
			4:10,
			111:50,
			112:50,
			1111: 50,
			1112: 50,
			1113: 50}
	# -------------------------------------------------------------------
	# user가 몇초에 한번씩 REQ 보낼 지 / float
	request_interval_sec = {1:1.0,
							2:1.0,
							3:1.0,
							4:1.0,
							111:1.0,
							112:1.0,
							1111: 1.0,
							1112: 1.0,
							1113: 1.0}
	# -------------------------------------------------------------------
	# USER가 총 몇개의 REQ를 보낼지...
	# 중간에 CTRL+C로 종료하면 REQ-RES 짝이 안맞는 경우 발생해서 이렇게 수정.
	max_req = {1:30,
				2:30,
				3:30,
				4:30,
				111:200,
				112:200,
				1111: 200,
				1112: 200,
				1113: 200}
	# -------------------------------------------------------------------
	def __init__(self):
		pass
	# -------------------------------------------------------------------
	def get_C(self, p):
		return self.C_sec[p]

	def get_img_name_ap1(self, p):
		return self.img_name_ap1[p]

	def get_img_name_ap2(self, p):
		return self.img_name_ap2[p]        

	def get_cont_name(self, p):
		return self.container_name[p]

	def get_req_int(self, p):
		return self.request_interval_sec[p]

	def get_ho_cnt(self, p):
		return self.ho_cnt[p]

	def get_predetermined_migr(self, p):
		return self.predetermined_migr[p]

	def get_checkpoint_name(self, p):
		return self.checkpoint_name[p]

	def get_summary(self, p):
		return self.C_sec[p], self.l_diff_bit[p], self.l_check_bit[p], \
				self.l_log_bit[p], self.t_replay_sec[p], self.th_bps[p]

	def get_final_dir_name(self, p):
		return self.final_dir_name[p]

	def get_max_req(self, p):
		return self.max_req[p]

	def get_replay_sec(self, p):
		return self.t_replay_sec[p]

	def get_diff_bit(self, p):
		return self.l_diff_bit[p]

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
		#return len(self.C_sec)
		my_keys = list(self.C_sec.keys())
		return max(my_keys)

	def get_ids(self):
		return list(self.C_sec.keys())
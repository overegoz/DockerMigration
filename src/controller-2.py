#-*- encoding: utf8 -*-
import socket 
import time
import signal, os
import datetime
import common



my_name = common.controller_name

# listen 소켓 생성
local_ip, local_port = common.ip[my_name], common.port[my_name]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((local_ip, local_port)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

def handler(signum, frame):  # CTRL+C 시그널 핸들러 만들기
	print(common.sigint_msg)
	# 코드마다 마무리 작업이 달라서, common 파일로 옮기지 못함
	sock.close()  
	exit()

signal.signal(signal.SIGINT, handler)  # 시그널 핸들러 등록

# 시작했다는 것을 로그로 남기기
common.send_log(None, sock, my_name, my_name, common.start_msg)

# 현재, USER가 연결되어있는 AP
# 처음에는 모른다고 하고, logger가 HELO 메시지를 전해주면 setting
user_curr_ap = ""
user_old_ap = ""

while(True):
	"""
	컨트롤러는 
	1. Logger로 부터 주요 이벤트 수신(HELO, BYEE)
	2. Migration 발생하면 old AP로 부터 관련 데이터 수신하고,
		어떤 방식의 migr을 할지를 old AP와 new AP에게 알려주기
	"""
	# 메시지 수신
	recv_msg, addr = common.udp_recv(sock, my_name, common.bufsiz, common.SHORT_SLEEP)

	if len(recv_msg) > 0:  # 수신한 메시지가 있다면...
		words = recv_msg.split(common.delim)
		sender = words[0]
		# LOGGER로 부터 받은 메시지라면... HELO/BYEE 이벤트에 대한 것이지
		if sender == common.logger_name:
			cmd = words[1]
			if cmd == common.USER_HELLO:  # [CR1]
				target = words[2]
				if len(user_curr_ap) == 0:
					# 처음으로 association 하는거면, migr 필요없음
					user_curr_ap = target
				else:  # handover 발생해서 다른 AP로 이동했다 : migr 준비하자
					"""
					handover로 인해서, user가 new AP에게 HELO를 보냈다
					user는 BYE보다 HELO를 먼저 보내니까, migr 작업을 여기서 시작하자
					"""
					assert (user_curr_ap == common.ap1_name) and \
						(target == common.ap2_name)
					user_old_ap = user_curr_ap
					user_curr_ap = target

					# [CS1] oldAP에게 '['migr 판단에 필요한 정보']'를 요청
					send_msg = common.str2(my_name, common.INFO_REQ)
					common.udp_send(sock, my_name, user_old_ap, send_msg, common.SHORT_SLEEP)
					print(user_old_ap, "에게 마이그레이션 정보 요청")

				print('user_old_ap:', user_old_ap)
				print('user_curr_ap:', user_curr_ap)
			elif cmd == common.USER_BYE:  # [CR2]
				# 할 일 없음. 
				# user_curr_ap, user_old_ap 변수 처리는 HELO 메시지 경우에 처리함
				pass
			elif cmd == common.USER_EXIT:  # [CR4] 모두 초기화
				user_curr_ap, user_old_ap = "", ""
			else:
				assert False
		# [CR3] AP로 부터 받은 것이라면, 
		# old AP로 부터 migr 기법 결정에 필요한 정보를 받은것이겠지
		elif sender == common.ap1_name or sender == common.ap2_name:
			assert len(user_curr_ap) > 0 and len(user_old_ap) > 0
			assert sender == user_old_ap

			# <AP-X> <INF_RES> <프로파일 번호> <migr 판단에 필요한 정보, '-'로 구분>
			assert words[1] == common.INFO_RES
			profile = int(words[2])
			infos = words[3]  # AP가 보내온 정보, '-'로 구분된 문자열

			# 받은 정보를 기준으로 어떤 migr 기법이 최선인지 판단하기
			best_migr = ""
			if common.prof.get_predetermined_migr(profile) == common.MIGR_AUTO:
				# 최적의 migr 기법을 자동(AUTO)으로 선택하기
				best_migr = common.get_best_migr(infos)
			else:
				# 사전에 설정된 migr 기법이 있으면, 그것을 선택하기
				best_migr = common.prof.get_predetermined_migr(profile)

			print("마이그레이션 기법 결정: ", best_migr)
			assert len(best_migr) > 0

			# 최선의 migr 기법을 old AP와 new AP 에게 알려주기
			# 1. migr 출발지 준비시작! [CS3.1]
			common.udp_send(sock, my_name, user_old_ap, 
							common.str3(my_name, common.MIGR_SRC, best_migr),
							common.SHORT_SLEEP)
			# 2. migr 목적지 준비시작! [CS3.2]
			common.udp_send(sock, my_name, user_curr_ap, 
							common.str3(my_name, common.MIGR_DST, best_migr),
							common.SHORT_SLEEP)
		else:  # 오류!
			assert False

	else: # 수신한 메시지가 없으면, 그냥 패스!
		pass
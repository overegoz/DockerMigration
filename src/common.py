"""
- 공통으로 사용하는 값을 정의
- 참고: 도커가 인식하는 자신의 IP는 0.0.0.0이다
"""
import time
import datetime

# ip table
# 총 4대의 VM을 사용하자
# 1. controller + logger
# 2. user
# 3. ap-1 (+ EdgeServer 1)
# 4. ap-2 (+ EdgeServer 2)
controller_name = "controller"
logger_name = "logger"
user_name = "user"
ap1_name = "ap-1"
ap2_name = "ap-2"

ip = {controller_name : "127.0.0.1",
        logger_name : "127.0.0.1",
        user_name : "127.0.0.1",
        ap1_name : "127.0.0.1",
        ap2_name : "127.0.0.1"}

# port number
port = {controller_name : 2000,
        logger_name : 2001,
        user_name : 2002,
        ap1_name : 2003,
        ap2_name : 2004}

# directory
account = "daniel"
base_dir = "/home/" + account + "/migration/"
checkpoint_dir = base_dir + "CheckPoints/"
fullcopy_dir = base_dir + "FullCopyImages/"
diffcopy_dir = base_dir + "DiffCopyFiles/"
logreplay_dir = base_dir + "LogReplayRecords/"

# other
bufsiz = 1024
sigint_msg = "SIGINT handler called! Terminating...\n"
delim = " "
start_msg = "start"
LOGGER_SLEEP = 0.1
USER_REQ_INTERVAL = 1.0

def get_now():  # 현재 시간을 문자열로 리턴
	return datetime.datetime.now().strftime("%Y-%m-%m-%H-%M-%S-%f")
	
def send_log(from_whom, msg):
    # 로그 메시지 만들기
    log = from_whom + delim + get_now() + delim + msg
    # Logger에게 전송하기
    udp_send(logger_name, log)	
	
def udp_send(sock, to_whom, msg):
    sock.sendto(msg.encode(), (ip[to_whom], port[to_whom]))	

def udp_recv(sock, bufsize):
	try:
		bytes, addr = sock.recvfrom(bufsize) 
		# 수신 데이터 출력하기, decode 해서 string객체로 변환
		msg =  bytes.decode()
	except socket.error:
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		msg = ""

	return msg
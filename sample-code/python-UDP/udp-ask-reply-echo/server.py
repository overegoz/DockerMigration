"""
클라이언트는 REQ + 카운터 번호를 전달하고
서버는 RES + (동일한) 카운터 번호를 회신
"""
import socket 
import time
import signal, os
import datetime
"""
- 컨테이너는 기본적으로 0.0.0.0 IP 주소를 가진다. 따라서 서버 IP 주소를
  0.0.0.0 으로 설정해 줘야 한다.
- 포트 포워딩은 서버 수신 포트인 20002만 해 주면 된다.
"""
#localIP = "127.0.0.1"
localIP = "0.0.0.0"
localPort = 20002

bufferSize = 1024
RESPONSE_INTERVAL = 1.0
TIME_DIVIDER = 4.0  # 서버는 클라이언트 보다 더 빨리 반응하도록...

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((localIP, localPort)) 
sock.setblocking(0)  # non-blocking socket으로 만들기


def handler(signum, frame):
	print("SIGINT handler called\n")
	sock.close()
	exit()
	
def getNowString():
	return str(datetime.datetime.now())
	
signal.signal(signal.SIGINT, handler)

log = "SVR " + getNowString() + " Server starts!"
print(log)



while(True): 
	
	# 데이터 수신하기
	try:
		bytes, addr = sock.recvfrom(bufferSize) 
		time.sleep(RESPONSE_INTERVAL/TIME_DIVIDER)
		
		# 수신 데이터 출력하기	
		log = "SVR " + getNowString() + " Recv : " + bytes.decode()
		print(log)
		remoteIP, remotePort = addr[0], addr[1]
		words = bytes.decode().split(' ')
		if( words[0] != "HELO" ):
			#print("Recv: ", num)
			num = int(words[1])
			msg = "RES " + str(num)
			# 상대방에게 데이터 전송하기
			sock.sendto(msg.encode(), (remoteIP, remotePort))
			
			log = "SVR " + getNowString() + " Sent : " + msg
			print(log)
		else:
			pass
	except socket.error:
		time.sleep(RESPONSE_INTERVAL/TIME_DIVIDER)
		# 클라이언트로 부터 요청/질문을 받지 않으면 답변할 게 없음
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		log = "SVR " + getNowString() + " Recv : nothing"
		print(log)
		bytes = ""
		addr = ""	
	
	time.sleep(RESPONSE_INTERVAL/TIME_DIVIDER)


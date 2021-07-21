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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((localIP, localPort)) 
sock.setblocking(0)  # non-blocking socket으로 만들기


def handler(signum, frame):
	print("SIGINT handler called\n")
	sock.close()
	exit()

signal.signal(signal.SIGINT, handler)
print("Server start!")
counter = 0
while(True): 
	time.sleep(0.5)
	
	# 데이터 수신하기
	try:
		bytes, addr = sock.recvfrom(bufferSize) 
		# 수신 데이터 출력하기	
		print(datetime.datetime.now(), " Recv : ", bytes.decode())
		#print("FROM: ", addr)
		remoteIP, remotePort = addr[0], addr[1]
		num = int(bytes.decode().split(' ')[1])
		#print("Recv: ", num)
		msg = str(num+1) + " " + bytes.decode().split(' ')[2]
		
		time.sleep(0.5)
		# 상대방에게 데이터 전송하기
		sock.sendto(msg.encode(), (remoteIP, remotePort))
		#print("sent: ", msg)
	except socket.error:
		# 클라이언트로 부터 요청/질문을 받지 않으면 답변할 게 없음
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		print(datetime.datetime.now(), " Recv : nothing")
		bytes = ""
		addr = ""	
	
	


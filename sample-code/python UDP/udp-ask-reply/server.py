import socket 
import time
import signal, os

localIP = "127.0.0.1"
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

while(True): 
	time.sleep(0.5)
	
	# 데이터 수신하기
	try:
		bytes, addr = sock.recvfrom(bufferSize) 
		# 수신 데이터 출력하기	
		#print("MSG: ", bytes.decode())
		#print("FROM: ", addr)
		remoteIP, remotePort = addr[0], addr[1]
		num = int(bytes.decode().split(' ')[1])
		print("Recv: ", num)
		msg = str(num+1)
		
		time.sleep(0.5)
		# 상대방에게 데이터 전송하기
		sock.sendto(msg.encode(), (remoteIP, remotePort))
	except socket.error:
		# 클라이언트로 부터 요청/질문을 받지 않으면 답변할 게 없음
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		#print("recvfrom: nothing")
		bytes = ""
		addr = ""	
	
	


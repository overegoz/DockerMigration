import socket 
import time
import signal, os

localIP = "127.0.0.1"
localPort = 20002

remoteIP = "127.0.0.1"
remotePort = 20001

bufferSize = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((localIP, localPort)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

msg = "MSG from host B"

def handler(signum, frame):
	print("SIGINT handler called\n")
	sock.close()
	exit()

signal.signal(signal.SIGINT, handler)

while(True): 
	# 데이터 수신하기
	try:
		bytes, addr = sock.recvfrom(bufferSize) 
		# 수신 데이터 출력하기	
		print("MSG: ", bytes.decode())
		print("FROM: ", addr)
	except socket.error:
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		#print("recvfrom: nothing")
		bytes = ""
		addr = ""
	
	time.sleep(0.5)

	# 상대방에게 데이터 전송하기
	sock.sendto(msg.encode(), (remoteIP, remotePort))
	
	time.sleep(0.5)


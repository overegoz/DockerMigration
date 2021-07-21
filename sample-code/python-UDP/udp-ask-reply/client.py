import socket 
import time
import signal, os

localIP = "127.0.0.1"
localPort = 20001

serverIP = "127.0.0.1"
serverPort = 20002


bufferSize = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 주소와 IP로 Bind 
sock.bind((localIP, localPort)) 
sock.setblocking(0)  # non-blocking socket으로 만들기

def handler(signum, frame):
	print("SIGINT handler called\n")
	sock.close()
	exit()

signal.signal(signal.SIGINT, handler)
counter = 0
print("Client begins!")
while(True): 

	# 상대방에게 데이터 전송하기
	# bytes 객체로 변환해서 보내야 함
	msg = "INCR " + str(counter)
	
	sock.sendto(msg.encode(), (serverIP, serverPort))
	print("Sent : ", msg)
	
	time.sleep(0.5)
	
	try:
		bytes, addr = sock.recvfrom(bufferSize) 
		# 수신 데이터 출력하기	
		print("Recv : ", bytes.decode())  # decode 해서 string객체로 변환
		#print("FROM: ", addr)  # (string ip, int port)
		"""
		print("type(bytes): ", type(bytes))  # bytes
		print("type(bytes.decode()): ", type(bytes.decode()))  # string
		print("type(addr): ", type(addr))  # tuple
		print("type(addr[0]): ", type(addr[0]))  # string
		print("type(addr[1]): ", type(addr[1]))  # int
		"""
		
		# 서버로 부터 응답을 받았을 경우에만 숫자를 변경하고
		# 서버가 보내준 숫자를 그대로 사용함
		counter = int(bytes.decode())
	except socket.error:
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		print("Recv : nothing")
		bytes = ""
		addr = ""
	
	time.sleep(0.5)

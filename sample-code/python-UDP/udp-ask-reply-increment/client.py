import socket 
import time
import signal, os
import datetime

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
iter = 0
print("Client begins!")
while(True): 

	# 상대방에게 데이터 전송하기
	# bytes 객체로 변환해서 보내야 함
	msg = "INCR " + str(counter) + " /" + str(iter)
	sock.sendto(msg.encode(), (serverIP, serverPort))
	iter = iter + 1
	print(datetime.datetime.now(), " Sent : ", msg)
	
	time.sleep(0.5)
	
	try:
		bytes, addr = sock.recvfrom(bufferSize) 
		# 수신 데이터 출력하기	
		print(datetime.datetime.now(), " Recv : ", bytes.decode())  # decode 해서 string객체로 변환
		#print("FROM: ", addr)  # (string ip, int port)
		"""
		print("type(bytes): ", type(bytes))  # bytes
		print("type(bytes.decode()): ", type(bytes.decode()))  # string
		print("type(addr): ", type(addr))  # tuple
		print("type(addr[0]): ", type(addr[0]))  # string
		print("type(addr[1]): ", type(addr[1]))  # int
		"""
	except socket.error:
		# non-blocking recv: 빈손으로 리턴할때 예외가 발생하고, 이를 잡아줘야함
		print(datetime.datetime.now(), " Recv : nothing")
		bytes = ""
		addr = ""
		
	"""
	서버로 전달된 메시지는 큐잉 되어 있다가 결국은 전달된다.
	따라서, 서버가 응답할때만 counter를 증가하게 되면 동일한 숫자를 반복적으로
	서버에 전달하게 되어서 순서번호가 꼬이는 경우가 발생한다.
	그냥 서버가 답하든 말든 REQUEST를 보내는 방식으로 하자. 
	결국은 정상적으로 시간에 맞게 동작하게 된다.
	그리고, 이렇게 해야, REQEST에 대한 RESPONSE가 언제 도착했는지
	응답시간을 측정하기에도 좋다.
	"""	
	counter = counter + 1
	time.sleep(0.5)

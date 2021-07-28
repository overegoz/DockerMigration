import time
import os


# 리눅스 terminal command를 테스트
print('[ls] begins')
os.system('ls')
print('[ls] finished')

print('[file dump] begins')
os.system('ls > /tmp/ls_results.txt')
print('[file dump] finished')

print('[truncate] begins')
os.system('truncate --size=10MB /tmp/just.file')
print('[truncate] finishes')

print('[file dump] begins')
os.system('ls > ls_results.txt')
print('[file dump] finished')

cnt = 0
while(True): 
	time.sleep(1)
	print('COUNT: ', cnt)  # print 구문이 logs 명령어로 확인 가능?
	cnt += 1

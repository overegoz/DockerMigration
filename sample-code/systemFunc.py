import os

"""
os.system 함수는 blocking 함수임. 즉, 인주로 주어진 작업/명령이 끝나야 리턴함
https://stackoverflow.com/questions/54628681/why-does-os-system-block-program-execution
"""

"""
작업완료 후 done을 찍어주면, log 파일을 통해서 작업시간을 계산하는데 유용할듯
"""
os.system('mkdir python-created-folder')
print('done')

os.system('truncate -s 3M my.file')  # 윈도우에서는 동작하지 않음
print('done')
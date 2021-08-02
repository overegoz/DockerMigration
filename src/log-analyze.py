import os
import time
import common  # 여기서 Profile 클래스 인스턴스도 하나 생성함

# ------------------------------------------------------------
# 폴더 내의 파일 목록 읽기
path_dir = './logs'  # 로그 파일이 저장된 폴더
file_list = os.listdir(path_dir)
nItems = len(file_list)
#print(nItems, ' : ', file_list)

# ------------------------------------------------------------
# 딕셔너리 구조로 만들기
file_dic = {}
for i in range(nItems):
    file_dic[i] = file_list[i]  # dict에 item 추가하기

#print(file_dic)
dic_keys = list(file_dic.keys())
dic_values = list(file_dic.values())
for i in range(nItems):
    print('{} : {}'.format(dic_keys[i], dic_values[i]))

# ------------------------------------------------------------
# 사용자에게 어떤 파일을 분석하고 싶은지 입력받기
choice = int(input('분석을 원하는 로그 파일의 번호를 입력하세요: '))
f_name = dic_values[choice]
print('User input: ', choice, ' = ', f_name)

# ------------------------------------------------------------
# 선택된 로그 파일 열기
f = open(f_name, 'r')

# ------------------------------------------------------------
# 분석 결과 출력하기

# 서비스 응답 시간 : 주의! 끝날때쯤에는 몇개의 REQ는 응답을 받지 못했을 수 있음
svc_req = {}  # 각 REQ 번호별로, 언제 sent 되었는지
svc_res = {}  # 각 RES 번호별로, 언제 recvd 되었는지
svc_rtt = {}  # 각 REQ 번호별로, 응답시간이 얼마나 되었는지, svc_req - svc_res

# 마이그레이션 관련
migr_begin, migr_finished = None, None  # migr에 걸린 시간을 측정하기 위함
migr_type = None  # 어떤 migr 기법을 사용했는지

# 프로파일/시나리오 관련
profile = None  # 어떤 Profile을 사용했는지

# 각종 파일의 크기
size_dic = {}  # 각종 파일의 크기를 저장할 딕셔너리
size_dic['img'] = None
size_dic['dump_img'] = None
size_dic['checkpoint'] = None
size_dic['diff'] = None
size_dic['log'] = None

# LogReplay 기법에서, replay 하는데 걸린 시간
replay_time_ap1, replay_time_ap2 = None, None

- 마이그레이션 기법
- 마이그레이션에 걸린 시간 (근데, 3가지 기법 모두 live migr 이라서, 서비스 단절 시간은 없음)
- 사용자의 request interval (Profile 클래스에서 얻어오기)
- 사용자의 on average response delay (다른 ENTITY 들이 udp send/recv 할때 sleep 하는데, 이것도 고려하기)
- 그 외
  . 이미지 파일 크기
  . FC인 경우, 복사 대상이 되는 dump한 이미지 파일 크기
  . FC, DC인 경우, checkpoint 크기
  . DC인 경우, diff 파일 크기
  . LR인 경우, log 파일 크기
  . LR인 경우, action을 수행하는데 걸린 시간 (ES는 "ReplayTime" 이라는 로그를 남김...)
  . 프로파일 번호가 몇번 이었는지

# ------------------------------------------------------------
# 파일 닫기
f.close()
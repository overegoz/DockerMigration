import common

class Profile:

    # 공통 소요시간
    C_sec = ['test']
    # diff 파일 전체 크기
    l_diff_bit = ['test']
    # checkpoint 파일 전체 크기
    l_check_bit = ['test']
    # log 파일 크기  
    l_log_bit = ['test']
    # log-replay에 걸리는 시간
    t_replay_sec = ['test']
    # effective throughput (bits/sec)
    th_bps = ['test']
    # 특정한 migr 기법을 강제하고 싶을때: MIGR_FC,DC,LR,AUTO 
    force = ['test']
    # 도커 이미지 이름 : 최초로 실행하는 이미지 이름
    img_name_ap1 = ['test']
    # 도커 이미지 이름 : migr 목적지에서 실행하는 이미지 이름
    img_name_ap1 = ['test']
    # 컨테이너 이름
    cont_name ['test'] 
    # 체크포인트 이름
    checkpoint_name = ['test']
    # user가 몇번의 REQ를 보낸 후 handover 할지
    ho_cnt = ['test']
    # user가 몇초에 한번씩 REQ 보낼 지
    req_int = ['test']
    
    def __init__(self):
        pass

    def get_C(p):
        return C_sec[p]

    def get_img_name_ap1():
        return img_name_ap1[p]

    def get_img_name_ap2():
        return img_name_ap2[p]        

    def get_cont_name():
        return cont_name[p]

    def get_req_int(p):
        return req_int[p]

    def get_ho_cnt(p):
        return ho_cnt[p]

    def id_min():
        # 프로필 -1번 : 도커 없이 실행
        # 프로필 0번 : 도커 있지만 migr 없음
        return -1

    def id_max():
        return len(C_sec)
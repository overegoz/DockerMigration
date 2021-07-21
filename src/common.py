"""
- 공통으로 사용하는 값을 정의
- 참고: 도커가 인식하는 자신의 IP는 0.0.0.0이다
"""

# ip table
ip = {"controller" : "192.168.0.113",
        "logger" : "192.168.0.113",
        "user" : "192.168.0.113",
        "host-a" : "192.168.0.113",
        "host-b" : "192.168.0.114"}

# port number
port = {"controller" : 2000,
        "logger" : 2001,
        "user" : 2002,
        "host-a" : 2003,
        "host-b" : 2004}

# directory
account = "daniel"
base_dir = "/home/" + account + "/migration/"
checkpoint_dir = base_dir + "CheckPoints/"
fullcopy_dir = base_dir + "FullCopyImages/"
diffcopy_dir = base_dir + "DiffCopyFiles/"
logreplay_dir = base_dir + "LogReplayRecords/"

# test
#print(ip["controller"])
#print(port["controller"])
#print(checkpoint_dir)
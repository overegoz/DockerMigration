

# ip table
ip = {"controller":"192.168.0.0",
        "logger":"192.168.0.0",
        "user":"192.168.0.0",
        "host-a":"192.168.0.0",
        "host-b":"192.168.0.0"}

# port number
port = {"controller":2000,
        "logger":2001,
        "user":2002,
        "host-a":2003,
        "host-b":2004}

# directory
base_dir = "/home/daniel/migration/"
checkpoint_dir = base_dir + "CheckPoints/"
fullcopy_dir = base_dir + "FullCopyImages/"
diffcopy_dir = base_dir + "DiffCopyFiles/"
logreplay_dir = base_dir + "LogReplayRecords/"

# test
#print(ip["controller"])
#print(port["controller"])
#print(checkpoint_dir)
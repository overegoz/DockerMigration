#!/bin/bash

# 880mbit로 해야 100MB/s 나옴
tc qdisc add dev enp0s3 root tbf rate 900mbit burst 1024kbit latency 10ms
#!/bin/bash

# 880mbit로 해야 100MB/s 나옴
# latency: packets with higher latency get dropped (딜레이 상한선)
tc qdisc add dev enp0s3 root tbf rate 880mbit burst 1024kbit latency 1000ms
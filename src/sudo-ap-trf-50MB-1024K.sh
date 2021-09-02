#!/bin/bash

# 440mbit로 해야 50MB/s 나옴
# latency: packets with higher latency get dropped (딜레이 상한선)
tc qdisc add dev enp0s3 root tbf rate 440mbit burst 1024kbit latency 1000ms
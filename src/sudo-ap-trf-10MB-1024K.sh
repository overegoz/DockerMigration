#!/bin/bash

# 88mbit로 해야 10MB/s가 나옴
# latency: packets with higher latency get dropped (딜레이 상한선)
tc qdisc add dev enp0s3 root tbf rate 88mbit burst 1024kbit latency 1000ms
#!/bin/bash

# 88mbit로 해야 10MB/s가 나옴
tc qdisc add dev enp0s3 root tbf rate 90mbit burst 1024kbit latency 100ms
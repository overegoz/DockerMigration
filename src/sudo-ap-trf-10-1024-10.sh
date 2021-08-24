#!/bin/bash

tc qdisc add dev enp0s3 root tbf rate 80mbit burst 1024kbit latency 10ms
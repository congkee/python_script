# coding: utf-8
import re
import threading
import socket
import requests
import time
import json


def get_ip():
    apollo_url = []
    ip_all = []
    ip_exclude = []
    for url in apollo_url:
        r = requests.get(url).json()['content']
        r = re.findall(r'[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}', r)
        ip_all = list(set(ip_all).union(set(r)))  # 不同环境ip列表并集
    ip_all = list(set(ip_all).difference(set(ip_exclude)))  # 排除不需要检测的机器,列表差集

    # print(ip_all)
    return ip_all


def push_falcon(is_connect, ip):
    ts = int(time.time())
    payload = [
        {
            "endpoint": "iptables_ssh",
            "metric": "iptables_ssh",
            "timestamp": ts,
            "step": 60,
            "value": is_connect,
            "counterType": "GAUGE",
            "tags": "ipinfo={ip},role=iptables_ssh_check".format(ip=ip),
        },
    ]

    requests.post("http://127.0.0.1:1988/v1/push", data=json.dumps(payload))


def ssh_check(ip):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    if sk.connect_ex((ip, 55888)):
        is_connect = 1
    else:
        is_connect = 0
    push_falcon(is_connect, ip)


def run_thread():
    thread_list = []
    for i in get_ip():
        t = threading.Thread(target=ssh_check, args=(i,))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()


if __name__ == '__main__':
    run_thread()
    # get_ip()

# coding: utf-8
"""
用于监测iptables INPUT规则变动,并指出具体的变动规则
"""
import os
import subprocess
import time
import json


# import requests


def old_rules():
    """
    防火墙规则记录,如果没有记录就创建到iptables_rules_txt
    """
    iptables_rules_txt = "/tmp/iptables_rules_txt"
    old_rules_list = []
    if os.path.isfile(iptables_rules_txt):
        with open(iptables_rules_txt, 'r') as f:
            for line in f:
                old_rules_list.append(line.strip())
    else:
        subprocess.Popen('iptables -nL INPUT > /tmp/iptables_rules_txt', shell=True).wait()
        with open(iptables_rules_txt, 'r') as f:
            for line in f:
                old_rules_list.append(line.strip())
    return old_rules_list


def new_rules():
    """
    执行iptables -nL INPUT 的结果
    """
    rules = subprocess.Popen('iptables -nL INPUT ', shell=True, stdout=subprocess.PIPE).communicate()
    new_rules_list = (rules[0].strip().split('\n'))
    return new_rules_list


def diff_rules():
    diff_add = list(set(new_rules()).difference(set(old_rules())))
    diff_del = list(set(old_rules()).difference(set(new_rules())))

    if len(diff_add) != 0:
        status = "新增规则"
        value = 0
        change_rules = diff_add
    elif len(diff_del) != 0:
        status = "删除规则"
        value = 0
        change_rules = diff_del
    else:
        status = ""
        value = 1
        change_rules = []
    data = {
        "status": status,
        "value": value,
        "change_rules": change_rules
    }

    return data


def push_falcon():
    ts = int(time.time())
    data = diff_rules()
    # hostname = subprocess.Popen('cat /usr/local/falcon-agent/config/cfg.json | grep hostname | awk -F "\"" "{print $4}"', shell=True, stdout=subprocess.PIPE).communicate()
    hostname = "test"
    push_data = {
        "endpoint": hostname,
        "metric": "iptables_rule",
        "timestamp": ts,
        "step": 60,
        "value": data['value'],
        "counterType": "GAUGE",
        "tags": 'change_rules="{status}{change_rules}'.format(change_rules=data['change_rules'], status=data['status']),
    }
    print(push_data)
    # requests.post("http://127.0.0.1:1988/v1/push", data=push_data)


if __name__ == '__main__':
    push_falcon()

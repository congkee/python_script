#!/usr/bin/python2.7
# coding: utf-8
"""
用于监测iptables INPUT规则变动,并记录具体的变动规则
"""
import json
import logging
import os
import subprocess
import time
import urllib2

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='/tmp/iptables_rule_change.log', level=logging.INFO, format=LOG_FORMAT)


def old_rules():
    """
    防火墙规则记录,如果没有记录就创建到iptables_rules_txt
    """
    iptables_rules_txt = "/tmp/iptables_rules_txt"
    old_rules_list = []
    if os.path.isfile(iptables_rules_txt):
        with open(iptables_rules_txt, 'r') as f:
            for line in f:
                old_rules_list.append(line.strip('\n'))
    else:
        subprocess.Popen('iptables -nL INPUT > /tmp/iptables_rules_txt', shell=True).wait()
        with open(iptables_rules_txt, 'r') as f:
            for line in f:
                old_rules_list.append(line.strip('\n'))
    return old_rules_list


def new_rules():
    """
    执行iptables -nL INPUT 的结果
    """
    rules = subprocess.Popen('iptables -nL INPUT ', shell=True, stdout=subprocess.PIPE).communicate()
    new_rules_list = (rules[0].strip().split('\n'))
    return new_rules_list


def diff_rules():
    new_list = new_rules()
    old_list = old_rules()
    diff_add = list(set(new_list).difference(set(old_list)))
    diff_del = list(set(old_list).difference(set(new_list)))

    if len(diff_add) == len(diff_del) == 0:
        value = 1
    else:
        value = 0
        logging.info("此次防火墙规则变动,删除了规则{diff_del},新增了规则{diff_add},请评估！！！".format(diff_del=diff_del, diff_add=diff_add))

    data = {
        "value": value
    }

    return data


def push_falcon():
    ts = int(time.time())
    diff_data = diff_rules()
    hostname = json.load(open('/usr/local/falcon-agent/config/cfg.json', 'r'))['hostname'].encode('utf-8')
    push_data = [{
        "endpoint": hostname,
        "metric": "iptables_rule_change",
        "timestamp": ts,
        "step": 60,
        "value": diff_data['value'],
        "counterType": "GAUGE",
        "tags": "role=iptables_rule_check"
    }]
    # requests.post("http://127.0.0.1:1988/v1/push", data=push_data) --python3+
    url = "http://127.0.0.1:1988/v1/push"
    request = urllib2.Request(url, json.dumps(push_data))
    urllib2.urlopen(request)

    subprocess.Popen('iptables -nL INPUT > /tmp/iptables_rules_txt', shell=True).wait()  # 将现有新规则写入到文件,用作下次对比的旧规则


if __name__ == '__main__':
    push_falcon()

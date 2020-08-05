# coding: utf-8
import requests

"""
1.比较堡垒机里面的主机和falcon中all_host组中主机,依赖从堡垒机导出的
"""
falcon_url = "http://127.0.0.1:8088"
headers = {'user-agent': 'python'}


class User(object):
    """登录验证"""

    @staticmethod
    def login_auth():
        api = "/api/v1/user/login"
        params = {
            "name": "rain",
            "password": "o0o0oo0"
        }
        r = requests.post(falcon_url + api, data=params)
        r = r.json()

        api_token = '{"name":"' + r['name'] + '", "sig":"' + r['sig'] + '"}'
        falcon_header = {
            "Apitoken": api_token,
            "X-Forwarded-For": "127.0.0.1",
            "Content-Type": "application/json",
            "name": r['name'],
            "sig": r['sig']
        }

        return falcon_header


class HostGroup(object):
    def __init__(self, grp_id=None):
        self.grp_id = grp_id

    def get_hostgroup_info(self):
        """根据hostgroup_id获取具体主机信息"""
        api = "/api/v1/hostgroup/{hostgroup_id}".format(hostgroup_id=self.grp_id)
        r = requests.get(falcon_url + api, headers=User.login_auth()).json()
        return r

    @staticmethod
    def hostgroup_list():
        """主机组列表"""
        api = "/api/v1/hostgroup"
        r = requests.get(falcon_url + api, headers=User.login_auth()).json()
        return r


def load_dict_from_file(filepath):
    _dict = {}
    try:
        with open(filepath, 'r') as dict_file:
            for line in dict_file:
                (key, value) = line.strip().split('\t')
                _dict[key] = value
    except IOError as ioerr:
        print("文件 %s 不存在" % (filepath))
    # new_dict = {v: k for k, v in _dict.items()}
    return _dict


if __name__ == '__main__':
    grp_name = "all_agent"
    host_to_ip = load_dict_from_file('/home/rain/all_host')
    jsp_list = list(host_to_ip.keys())
    hostgrop_list = HostGroup.hostgroup_list()
    for grp in hostgrop_list:
        if grp_name == grp['grp_name']:
            grp_id = grp['id']
    falcon_agent_hosts = HostGroup(grp_id).get_hostgroup_info()['hosts']
    agent_hosts_list = []
    for hostname in falcon_agent_hosts:
        agent_hosts_list.append(hostname['hostname'])
    diff_list = list(set(jsp_list).difference(set(agent_hosts_list)))

    for i in diff_list:
        print(i, host_to_ip[i])
        # print(i)
        # print(host_to_ip[i])
    print(len(diff_list))

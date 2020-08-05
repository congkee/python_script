# coding: utf-8

import requests

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


class Template(object):
    def __init__(self, temp_name):
        self.temp_name = temp_name
        self.temp_id = False

    def get_template_id(self):
        """根据服务名称获取template_id"""
        api = "/api/v1/template"
        r = requests.get(falcon_url + api, headers=User.login_auth()).json()['templates']

        for i in r:
            if i['template']['tpl_name'] == self.temp_name:
                self.temp_id = i['template']['id']
        return self.temp_id

    def get_hostgroups_list(self, temp_id):
        """根据template_id获取绑定的hostgroups,可以是多个"""
        api = "/api/v1/template/{temp_id}/hostgroup".format(temp_id=temp_id)
        r = requests.get(falcon_url + api, headers=User.login_auth()).json()
        return r

    def create_template(self, action=99):
        """创建模板"""
        api = "/api/v1/template"
        temp_data = {
            "parent_id": 0,
            "name": self.temp_name,
            "action_id": action
        }
        r = requests.post(falcon_url + api, data=temp_data, headers=User.login_auth()).json()
        return r

    def create_templata_action(self):
        """暂时根据template_info获取acticon_id=99"""
        pass

    def template_info(self, temp_id):
        """根据模板id获取详细信息"""
        api = "/api/v1/template/{temp_id}".format(temp_id=temp_id)
        r = requests.get(falcon_url + api, headers=User.login_auth())
        return r


class HostGroup(object):
    def __init__(self, grp_id=None):
        self.grp_id = grp_id

    def get_hostgroup_info(self):
        """根据hostgroup_id获取具体主机信息"""
        api = "/api/v1/hostgroup/{hostgroup_id}".format(hostgroup_id=self.grp_id)
        r = requests.get(falcon_url + api, headers=User.login_auth()).json()
        return r

    def add_hosts_to_hostgroup(self, add_hosts):
        """添加主机到主机组"""
        api = "/api/v1/hostgroup/host"
        data = {
            "hosts": add_hosts,
            "hostgroup_id": self.grp_id
        }
        r = requests.post(falcon_url + api, data=data, headers=User.login_auth())
        return r

    @staticmethod
    def hostgroup_list():
        """主机组列表"""
        api = "/api/v1/hostgroup"
        r = requests.get(falcon_url + api, headers=User.login_auth())
        return r

    def create_hostgroup(self, name):
        """创建一个主机组"""
        api = "/api/v1/hostgroup"
        data = {
            "name": name
        }
        r = requests.post(falcon_url + api, data=data, headers=User.login_auth())
        return r

    def bind_temp_to_grp(self, tpl_id):
        """绑定模板到主机组"""
        api = "/api/v1/hostgroup/template"
        data = {
            "tpl_id": tpl_id,
            "grp_id": self.grp_id
        }
        r = requests.post(falcon_url + api, data=data, headers=headers)
        return r


class Strategy(object):
    def __init__(self):
        pass

    def create_strategy(self, tmp_id, port, service):
        """创建告警策略"""
        api = "/api/v1/strategy"
        data = {
            'metric': 'net.port.listen',
            'tags': 'port={port}'.format(port=port),
            'max_step': 2,
            'priority': 0,
            'func': 'all(#2)',
            'op': '!=',
            'right_value': '1',
            'note': '严重 - {service}服务异常！'.format(service=service),
            'run_begin': '',
            'run_end': '',
            'tpl_id': tmp_id
        }
        r = requests.post(falcon_url + api, data=data, headers=User.login_auth())
        return r


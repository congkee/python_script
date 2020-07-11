# coding: utf-8

import requests


consul_service_url = "http://consul_service_url/v1/catalog/service/"
consul_services_url = "http://consul_service_url/v1/catalog/services"


def load_dict_from_file(filepath):
    _dict = {}
    try:
        with open(filepath, 'r') as dict_file:
            for line in dict_file:
                (key, value) = line.strip().split('\t')
                _dict[key] = value
    except IOError as ioerr:
        print("文件 %s 不存在" % (filepath))
    new_dict = {v: k for k, v in _dict.items()}
    return new_dict


def services():
    services_all = requests.get(consul_services_url)
    r = services_all.json()
    services_list = []
    for i in r:
        services_list.append(i)
    return services_list


def service_info(service):
    ip_to_host = load_dict_from_file('hosts')
    service_host = requests.get(consul_service_url + service)
    r = service_host.json()
    service_address = []
    service_name = ""
    service_port = ""
    service_hosts = []
    for i in r:
        service_name = i['ServiceName']
        service_port = i['ServicePort']
        address = i['ServiceAddress']
        service_address.append(address)
        if address in ip_to_host:
            host_value = ip_to_host[address]
            service_hosts.append(host_value)
    service_address = list(set(service_address))  # ip去重
    service_hosts = list(set(service_hosts))  # host去重

    data = {
        "service_name": service_name,
        "service_info": {
            "service_port": service_port,
            "service_address": service_address,
            "service_hosts": service_hosts
        }
    }
    # print(data)
    return data

from falcon_data import *
import consul_data


def check_falcon():
    services = consul_data.services()
    for service in services:
        temp = Template(service)
        temp_id = temp.get_template_id()
        consul_hosts = consul_data.service_info(service)['service_info']['service_hosts']
        if temp_id:
            grp_info = temp.get_hostgroups_list(temp_id)
            if len(grp_info['hostgroups']) > 0:
                for grp_id in grp_info['hostgroups']:
                    host_info = HostGroup(grp_id)
                    hosts = host_info.get_hostgroup_info()['hosts']
                    falcon_hosts = []
                    for host in hosts:
                        falcon_hosts.append(host['hostname'])
                    check_hosts = list(set(consul_hosts).difference(set(falcon_hosts)))
                    if len(check_hosts) > 0:
                        print("\033[1;31;40m {service}该应用绑定主机不全,以下主机{hosts}未绑定！\033[0m".format(service=service,
                                                                                               hosts=check_hosts))
                        host_info.add_hosts_to_hostgroup(consul_hosts)  # 绑定主机
                        print("{service}该应用绑定主机已补全！")
                    else:
                        print("{service}该应用监控配置正常".format(service=service))
            else:
                print("\033[1;31;40m {service}该应用模板以创建,但未绑定主机组！\033[0m".format(service=service))
                hostgroup = HostGroup()
                create_grp = hostgroup.create_hostgroup("{service}-hosts".format(service=service))
                print("{grp_name}已创建".format(grp_name=create_grp['grp_name']))

                add_hosts = hostgroup.add_hosts_to_hostgroup(consul_hosts)
                print("{hosts}已加入模板".format(hosts=add_hosts['message']))

                bind_info = hostgroup.bind_temp_to_grp(temp_id)
                print("{grp_id}主机组已绑定{temp_id}模板".format(grp_id=bind_info['grp_id'], temp_id=bind_info['tpl_id']))
        else:
            print("\033[1;31;40m {service}该应用模板不存在,请创建！\033[0m".format(service=service))
            temp_name = Template(service)
            create_temp = temp_name.create_template()
            Strategy.create_strategy(create_temp['id'],
                                     consul_data.service_info(service)['service_info'][
                                         'service_port', service])
            hostgroup = HostGroup()
            create_grp = hostgroup.create_hostgroup("{service}-hosts".format(service=service))
            print("{grp_name}已创建".format(grp_name=create_grp['grp_name']))

            add_hosts = hostgroup.add_hosts_to_hostgroup(consul_hosts)
            print("{hosts}已加入模板".format(hosts=add_hosts['message']))

            bind_info = hostgroup.bind_temp_to_grp(temp_id)
            print("{grp_id}主机组已绑定{temp_id}模板".format(grp_id=bind_info['grp_id'], temp_id=bind_info['tpl_id']))


if __name__ == '__main__':
    check_falcon()

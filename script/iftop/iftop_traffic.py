# !/usr/bin/env python

import subprocess
import re, time, datetime, json
from itertools import groupby


class trafficFeatureExtract():
    def __init__(self):
        self.nic, self.ip = self.__get_nic_and_ip()
        print(self.nic, self.ip)

    def get_traffic_raw_data(self):
        start_time = int(time.time())
        output = subprocess.Popen(["iftop", "-i", self.nic, "-N", "-n", "-P", "-t", "-s", "10"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        res = output.stdout.read().split('\n')
        #print(res)
        last_list=[]
        if len(res) > 3:
            record_list=[]
            for line in res:
                #if isinstance(line, str) and re.match('^\s{3}\d{1,}', line):
                if isinstance(line, str) and re.match('.*(<=|=>).*', line):
                    record_list.append(line)
            for index, record in enumerate(record_list):
                if index % 2 != 0:
                    record_list[index-1]+= record
            #print(record_list[::2])
            for line in record_list[::2]:
                line_split=line.split()
                #print(line_split)
                record_dict={}
                record_dict.setdefault('start_time',start_time)
                l_addr=line_split[1]
                record_dict.setdefault('l_addr',l_addr)
                l_ip_port_split=l_addr.split(':')
                record_dict.setdefault('l_ip',l_ip_port_split[0])
                if len(l_ip_port_split) == 2:
                    record_dict.setdefault('l_port',l_ip_port_split[1])
                else:
                    record_dict.setdefault('l_port', '')
                record_dict.setdefault('l_s_last2',self.replace_net_unit(line_split[3]))
                record_dict.setdefault('l_s_last10',self.replace_net_unit(line_split[4]))
                record_dict.setdefault('l_s_last40',self.replace_net_unit(line_split[5]))
                record_dict.setdefault('l_s_cumulative',self.replace_net_unit(line_split[6]))
                r_addr=line_split[7]
                record_dict.setdefault('r_addr',r_addr)
                r_ip_port_split=r_addr.split(':')
                record_dict.setdefault('r_ip',r_ip_port_split[0])
                if len(l_ip_port_split) == 2:
                    record_dict.setdefault('r_port',r_ip_port_split[1])
                else:
                    record_dict.setdefault('r_port', '')
                record_dict.setdefault('r_r_last2',self.replace_net_unit(line_split[9]))
                record_dict.setdefault('r_r_last10',self.replace_net_unit(line_split[10]))
                record_dict.setdefault('r_r_last40',self.replace_net_unit(line_split[11]))
                record_dict.setdefault('r_r_cumulative',self.replace_net_unit(line_split[12]))
                record_dict.setdefault('l_ip_to_r_addr',record_dict['l_ip']+'-->'+ record_dict['r_ip'])
                record_dict.setdefault('r_ip_to_l_addr',record_dict['r_ip']+'-->'+ record_dict['l_ip'])
                last_list.append(record_dict)
        return last_list

    def __get_nic_and_ip(self):
        output = subprocess.Popen(["ip", "-4", "route", "get", "8.8.8.8"],
                                  stdout=subprocess.PIPE)
        res = output.stdout.read()
        line1 = res.split('\n')
        if len(line1) > 0:
            sep_info = line1[0].split()
            #print(sep_info)
            if len(sep_info) == 7:
                return (sep_info[-3], sep_info[-1])

    def replace_net_unit(self,metric_str):
        if isinstance(metric_str, str):
            time_parse_list = [''.join(list(g)) for k, g in groupby(metric_str, key=lambda x: x in [ str(i) for i in range(10) ] + ['.'])]
            #print(time_parse_list)
            metric_map = {'b':1, 'kb': 1024, 'mb': 1024 ** 2, 'gb': 1024 ** 3}
            return int(float(time_parse_list[0]) * metric_map[time_parse_list[1].lower()])


if __name__ == '__main__':
    tfe = trafficFeatureExtract()
    start_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')
    print(start_time)
    res = tfe.get_traffic_raw_data()
    output_file='/tmp/iftop_statstics_%s.txt' % start_time
    print(output_file)
    for line in res:
        with open(output_file, 'a+') as f:
            f.write(json.dumps(line) + '\n')

    cmd = 'find /tmp -type f -name "*iftop_statstics_*" -mtime +5 | xargs rm -rf'
    del_old_file_res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = del_old_file_res.communicate()[0]
    print(output)
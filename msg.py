# -*- coding: UTF-8 -*-

import json
import errno

class Message:
    def __init__(self):
        self.info = {
            'user_name' : '',
            'type' : '',
            'dev_name' : '',
            'rsp_value' : 0,
            'rsp_user_list' : []
        }

    def create_msg_req_dev(self, user_name, dev_name):
        self.info['type'] = 'req_dev'
        self.info['user_name'] =user_name
        self.info['dev_name'] = dev_name

    def create_msg_free_dev(self, user_name, dev_name):
        self.info['type'] = 'free_dev'
        self.info['user_name'] =user_name
        self.info['dev_name'] = dev_name

    def create_msg_query_dev(self):
        self.info['type'] = 'query_dev'

    def create_msg_kick_dev(self, dev_name):
        self.info['type'] = 'kick_dev'
        self.info['dev_name'] = dev_name

    def create_version_req(self, version):
        self.info['type'] = 'version_req'
        self.info['version'] = version

    def create_version_down(self, version):
        self.info['type'] = 'version_down'
        self.info['version'] = version

    def get_version(self):
        return self.info['version']

    def create_msg_rsp(self, err_no):
        self.info['type'] = 'rsp_status'
        self.info['rsp_value'] = err_no

    def msg_rsp_add_user(self, user_list):
        self.info['type'] = 'rsp_status'
        self.info['rsp_user_list'] = user_list

    def msg_rsp_add_version(self, version, ftp_info):
        self.info['version'] = version
        self.info['ftp_info'] = ftp_info

    def msg_rsp_status(self):
        if self.info['type'] == 'rsp_status':
            return self.info['rsp_value']
        else:
            return errno.EINVAL

    def msg_get_user_list(self):
        return self.info['rsp_user_list']

    def msg_get_ftp_info(self):
        return self.info['ftp_info']

    def msg_decode(self, json_str):
        if(json_str):
            self.info = json.loads(json_str)

    def msg_encode(self):
        return json.dumps(self.info)

    def reset(self):
        self.info = {}

    def dump(self):
        return repr(self.info)
# -*- coding: UTF-8 -*-

import socket
import time
import errno
import os
import logging
from msg import Message 

class Client:
    def __init__(self):
        self.users = {}
        self.user_name = ''
        self.version = '0.1'
        self.file_name = 'msg_queue.exe'

    def set_log_level(self):
        LOG_FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s %(lineno)d	:%(message)s'
        if os.path.exists('client_debug.txt'):
            logging.basicConfig(filename='client.log', level=logging.DEBUG, format=LOG_FORMAT)
        else:
            logging.basicConfig(level=logging.CRITICAL, format=LOG_FORMAT)

    def connect(self, ip, port = 9421):
        self.sock = socket.socket()
        self.sock.settimeout(1)
        self.sock.connect((ip, port))

    def disconnect(self):
        self.sock.close()

    def version_check(self):
        msg = Message()
        msg.create_version_req(self.version)
        json_str = msg.msg_encode()
        msg.reset()
        try:
            self.sock.sendall(json_str.encode())
            json_str = self.sock.recv(1000).decode()
        except Exception:
            return False, None

        msg.msg_decode(json_str)
        version = msg.get_version()
        if version == self.version:
            return True, None
        else:
            return False, msg.msg_get_ftp_info()

    def download_new_version(self, ftp_info):
        b = open('upgrade.bat','w')
        TempList = '@echo off\n'
        TempList += 'echo Ready to update..\n'
        TempList += 'timeout /t 1 /nobreak\n' 
        TempList += ('del %s\n') % (self.file_name)
        TempList += ('echo open %s> ftp.txt\n') % (ftp_info['server_ip'])
        TempList += ('echo %s>> ftp.txt\n') % (ftp_info['username'])
        TempList += ('echo %s>> ftp.txt\n') % (ftp_info['password'])
        TempList += ('echo get %s>> ftp.txt\n') % (ftp_info['filename'])
        TempList += 'echo quit>>ftp.txt\n'
        TempList += 'ftp -s:ftp.txt\n'
        TempList += 'del ftp.txt\n'

        TempList += 'echo Finish...\n'
        TempList += 'timeout /t 3 /nobreak\n'
        TempList += 'exit'
        logging.debug(TempList)
        b.write(TempList)
        b.close()
        os.system('start upgrade.bat')  #show cmd windows

    def set_user_name(self, name):
        self.user_name = name

    def req_dev(self, dev_name):
        msg = Message()
        msg.create_msg_req_dev(self.user_name, dev_name)
        json_str = msg.msg_encode()
        logging.debug('req_dev %s' % json_str)
        msg.reset()
        try:
            self.sock.sendall(json_str.encode())
            json_str = self.sock.recv(1000).decode()
            msg.msg_decode(json_str)
        except Exception as err:
            return err

        return msg.msg_rsp_status()

    def free_dev(self, dev_name):
        msg = Message()
        msg.create_msg_free_dev(self.user_name, dev_name)
        json_str = msg.msg_encode()
        logging.debug('free_dev %s ' % json_str)
        msg.reset()
        try:
            self.sock.sendall(json_str.encode())
            json_str = self.sock.recv(1000).decode()
            msg.msg_decode(json_str)
        except Exception as err:
            return err

        return msg.msg_rsp_status()

    def kick_dev(self, dev_name):
        msg = Message()
        msg.create_msg_kick_dev(dev_name)
        json_str = msg.msg_encode()
        logging.debug('kick_dev %s' % json_str)
        msg.reset()
        try:
            self.sock.sendall(json_str.encode())
            json_str = self.sock.recv(1000).decode()
            msg.msg_decode(json_str)
        except Exception as err:
            return err

        return msg.msg_rsp_status()

    def query_dev(self):
        msg = Message()
        msg.create_msg_query_dev()
        json_str = msg.msg_encode()
        logging.debug('query %s' % json_str)
        msg.reset()
        try:
            self.sock.sendall(json_str.encode())
        except Exception as err:
            logging.debug(err)
            return False, []

        try:
            json_str = self.sock.recv(1000).decode()
        except Exception as err:
            logging.debug(err)
            return False, []

        logging.debug('rsp info : %s' % json_str)
        msg.msg_decode(json_str)
        if msg.msg_rsp_status() == 0:
            return True, msg.msg_get_user_list()
        else:
            return False, []

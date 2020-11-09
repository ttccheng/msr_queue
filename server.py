# -*- coding: UTF-8 -*-

import socket
import select
import errno
import sys
import logging
from msg import Message 
from datetime import datetime,timedelta,timezone

class Server:
    def __init__(self):
        self.users = {}
        self.dev_list = []
        self.max_dev_user = 5
        self.clear_day = 0
        self.client_version = '0.1'
        self.ftp_info = {}
        self.ftp_info['server_ip']  = '192.168.160.89'
        self.ftp_info['username']  = '8090'
        self.ftp_info['password']  = '8090'
        self.ftp_info['filename']  = 'msg_queue.exe'
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(funcName)s %(lineno)d	:%(message)s"
        logging.basicConfig(filename='server.log', level=logging.DEBUG, format=LOG_FORMAT)

    def init_connect(self, ip = '0.0.0.0', port = 9421, max_listen = 100):
        self.listen_sock = socket.socket()
        self.listen_sock.bind((ip, port))
        self.listen_sock.listen(max_listen)
        self.recv_size = 1000
        self.epoll_obj = select.epoll()
        self.epoll_obj.register(self.listen_sock, select.EPOLLIN)
        self.connections = {}

    def init_dev_list(self):
        self.dev_list.append({'name' : 'MSR-2',   'user_list' : []})
        self.dev_list.append({'name' : 'MSR-3',   'user_list' : []})
        self.dev_list.append({'name' : 'MSR-4',   'user_list' : []})
        self.dev_list.append({'name' : 'MSR-163', 'user_list' : []})

    def get_dev(self, dev_name):
        for dev in self.dev_list:
            if dev['name'] == dev_name:
                return dev
        return None

    def add_user_to_dev(self, user_name, dev_name):
        dev = self.get_dev(dev_name)
        if dev:
            if len(dev['user_list']) >= self.max_dev_user:
                return errno.ENOSPC
            if dev['user_list'].count(user_name) > 0 :
                return errno.EEXIST
            dev['user_list'].append(user_name)     
        else :
            return errno.ENOENT

        return 0
        
    def del_user_from_dev(self, user_name, dev_name):
        dev = self.get_dev(dev_name)
        if dev:
            if dev['user_list'].count(user_name) == 0 :
                return 0
            dev['user_list'].remove(user_name)
        else :
            return errno.ENOENT

        return 0

    def del_first_user_from_dev(self, dev_name):
        dev = self.get_dev(dev_name)
        if dev:
            if len(dev['user_list']) == 0 :
                return 0
            dev['user_list'].pop(0)
        else :
            return errno.ENOENT

        return 0

    def get_user_from_dev(self):
        dev_user_list = []
        for dev in self.dev_list:
            dev_info = {}
            dev_info['dev_name'] = dev['name']
            dev_info['user_list'] = dev['user_list']
            dev_user_list.append(dev_info)

        return 0, dev_user_list

    def process_client_msg(self, conn, msg):
        logging.debug(('recv msg : %s' % msg.dump()))
        rsp_msg = Message()
        rc = 0
        if msg.info['type'] == 'req_dev':
            rc = self.add_user_to_dev(msg.info['user_name'], msg.info['dev_name'])
            rsp_msg.create_msg_rsp(rc)
        elif msg.info['type'] == 'free_dev':
            rc = self.del_user_from_dev(msg.info['user_name'], msg.info['dev_name'])
            rsp_msg.create_msg_rsp(rc)
        elif msg.info['type'] == 'query_dev':
            rc, user_list = self.get_user_from_dev()
            rsp_msg.create_msg_rsp(rc)
            if rc == 0 :
                rsp_msg.msg_rsp_add_user(user_list)
        elif msg.info['type'] == 'kick_dev':
            rc = self.del_first_user_from_dev(msg.info['dev_name'])
            rsp_msg.create_msg_rsp(rc)
        elif msg.info['type'] == 'version_req':
            rsp_msg.create_msg_rsp(rc)
            rsp_msg.msg_rsp_add_version(self.client_version, self.ftp_info)

        json_str = rsp_msg.msg_encode()
        logging.debug(('rsp info : %s ' % json_str))
        conn.sendall(json_str.encode())

    def clear_user(self):
        tz_utc_8=timezone(timedelta(hours=8))
        now_day = datetime.now(tz = tz_utc_8).day
        if self.clear_day == 0:
            self.clear_day = now_day
        elif self.clear_day != now_day:
            for dev in self.dev_list:
                dev['user_list'].clear()
            self.clear_day = now_day

    def run(self):
        while True:
            self.clear_user()
            events = self.epoll_obj.poll(60)
            for fd, event in events:
                logging.debug('event triger fd = 0x%x event 0x%x' % (fd,event))
                if fd == self.listen_sock.fileno():
                    conn, addr = self.listen_sock.accept()
                    logging.info('User connect : %s' % repr(addr))
                    self.connections[conn.fileno()] = conn
                    self.epoll_obj.register(conn, select.EPOLLIN)
                else:
                    try:
                        fd_obj = self.connections[fd]
                        buffer = fd_obj.recv(self.recv_size)
                        json_str = buffer.decode()
                        if json_str : 
                            logging.debug("json_str = %s " % json_str)
                            msg = Message()
                            msg.msg_decode(json_str)
                            self.process_client_msg(fd_obj, msg)
                        else :
                            self.epoll_obj.unregister(fd)
                            self.connections[fd].close()
                            del self.connections[fd]
                            logging.info('empty close.. %u ' % (fd))

                    except ConnectionResetError:
                        self.epoll_obj.unregister(fd)
                        self.connections[fd].close()
                        del self.connections[fd]
                        logging.info('disconnect %d ' % fd)
                        
                    except BrokenPipeError:
                        self.epoll_obj.unregister(fd)
                        self.connections[fd].close()
                        del self.connections[fd]
                        logging.info('close %d' % fd)

                    except:
                        self.epoll_obj.unregister(fd)
                        self.connections[fd].close()
                        del self.connections[fd]
                        logging.info('unexcept error %u %s' %(fd, sys.exc_info()[0]))

    def close(self):
        self.listen_sock.close()
        self.epoll_obj.close()



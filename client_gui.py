# -*- coding: UTF-8 -*-

from tkinter import *
import tkinter.messagebox 
import hashlib
import time
from client import Client
import threading

LOG_LINE_NUM = 0

class Client_Gui():
    def __init__(self, gui_windows):
        self.gui_windows = gui_windows
        self.dev_list = []
        self.header_size = 3
        self.status = 'init'
        self.client = Client()
        self.query_time = 0
        self.client.set_log_level()

    def client_not_connected(self):
        if self.status == 'connected':
            return False
        else:
            return True

    def create_dev(self, name):
        dev = {}
        dev_list_row = 4
        dev['name'] = name
        dev['user_list'] = []
        dev['info_msg_box'] = False

        dev['header'] =  Label(self.gui_windows, text='', anchor=E, width=10)
        label_row =  0 + self.header_size + dev_list_row*len(self.dev_list)
        dev['header'].grid(row = label_row, column = 0)

        dev['show label'] =  Label(self.gui_windows, text=name + ' :', anchor=E, width=10)
        label_row =  1 + self.header_size + dev_list_row*len(self.dev_list)
        dev['show label'].grid(row = label_row, column = 0)

        dev['dev_req'] = Button(self.gui_windows, text='占用', bg='lightblue', width=14,
                                command=lambda :self.req_dev(name))

        dev['dev_req'].grid(row = label_row, column=1)

        dev['dev_free'] = Button(self.gui_windows, text='释放', bg='lightblue', width=14,
                                command=lambda :self.free_dev(name))
        dev['dev_free'].grid(row = label_row, column=2)

        dev['dev_kick'] = Button(self.gui_windows, text='强制释放', bg='lightblue', width=14,
                                command=lambda :self.kick_dev(name))
        dev['dev_kick'].grid(row = label_row, column=3)

        dev['using label'] =  Label(self.gui_windows, text='使用中 : ', anchor=E, width=10)
        label_row =  2 + self.header_size + dev_list_row*len(self.dev_list)
        dev['using label'].grid(row = label_row, column = 0)

        dev['using user'] =  Label(self.gui_windows, text='', anchor=W, width=45)
        label_row =  2 + self.header_size + dev_list_row*len(self.dev_list)
        dev['using user'].grid(row = label_row, column = 1, columnspan=3)

        dev['wait label'] =  Label(self.gui_windows, text='排队中 : ', anchor=E, width=10)
        label_row =  3 + self.header_size + dev_list_row*len(self.dev_list)
        dev['wait label'].grid(row = label_row, column = 0)

        dev['wait user'] =  Label(self.gui_windows, text='', anchor=W, width=45)
        label_row =  3 + self.header_size + dev_list_row*len(self.dev_list)
        dev['wait user'].grid(row = label_row, column = 1, columnspan=3)

        self.dev_list.append(dev)

    def get_dev(self, dev_name):
        for dev in self.dev_list:
            if dev['name'] == dev_name:
                return True, dev
        return False, None

    def set_init_window(self):
        windowwidth = 480
        windowhieight = 500
        screenwidth = self.gui_windows.winfo_screenwidth()
        screenheight = self.gui_windows.winfo_screenheight()
        windows_size = '%dx%d+%d+%d' % (windowwidth, windowhieight, (screenwidth - windowwidth)/2, (screenheight - windowhieight)/2)

        self.gui_windows.title('MSR Queue System %s' % (self.client.version))
        self.gui_windows.geometry(windows_size)

        self.server_ip_label = Label(self.gui_windows, text='Server IP:', anchor=E, width=10)
        self.server_ip_label.grid(row=0, column=0)

        self.server_ip_Text = Text(self.gui_windows, width=15, height=1)
        self.server_ip_Text.insert(CURRENT,'172.0.12.66')
        self.server_ip_Text.grid(row=0, column=1)

        self.status_label = Label(self.gui_windows, text='Disconnect', fg='red', width=15)
        self.status_label.grid(row=0, column=2)

        self.user_name_label = Label(self.gui_windows, text='Username:', anchor=E, width=10)
        self.user_name_label.grid(row=1, column=0)

        self.user_name_Text = Text(self.gui_windows, width=15, height=1)
        self.user_name_Text.grid(row=1, column=1)

        self.connect_Buttom = Button(self.gui_windows, text='连接', bg='lightblue', width=14, height=1, 
                                command=self.connect)
        self.connect_Buttom.grid(row = 1, column=2)

        self.connect_Buttom = Button(self.gui_windows, text='断开', bg='lightblue', width=14, height=1, 
                                command=self.disconnect)
        self.connect_Buttom.grid(row = 1, column=3)

        self.create_dev('MSR-2')
        self.create_dev('MSR-3')
        self.create_dev('MSR-4')
        self.create_dev('MSR-163')

        self.status_label.after(1000, self.status_label_update)

    def connect(self):
        server_ip = self.server_ip_Text.get(1.0,END).strip().replace('\n','')
        user_name = self.user_name_Text.get(1.0,END).strip().replace('\n','')
        if len(user_name) == 0:
            tkinter.messagebox.showinfo('Error', '用户名为空')
            return
        try:
            self.client.connect(server_ip)
            self.client.set_user_name(user_name)
        except:
            tkinter.messagebox.showinfo('Error', '连接服务器失败')
            return

        valid, ftp_info = self.client.version_check()
        if not valid : 
            if ftp_info:
                tkinter.messagebox.showinfo('Info', '准备更新')
                self.client.download_new_version(ftp_info)
                self.gui_windows.destroy()
                return
            else:
                tkinter.messagebox.showinfo('Error', '更新失败')

        self.status = 'connected'
        self.status_label.config(text = 'Connected')
        self.query_dev()
 
    def disconnect(self):
        if self.client_not_connected():
            return
        self.client.disconnect()
        self.status = 'init'
        self.client.set_user_name('')
        self.status_label.config(text = 'Disconnect')

    def req_dev(self, name):
        if self.client_not_connected():
            tkinter.messagebox.showinfo('错误', '未连接服务器')
            return
            
        if tkinter.messagebox.askyesno('提示', '确定占用 %s？' % (name)):
            self.client.req_dev(name)

        self.query_dev()
 
    def free_dev(self, name):
        if self.client_not_connected():
            tkinter.messagebox.showinfo('错误', '未连接服务器')
            return

        if tkinter.messagebox.askyesno('提示', '确定释放 %s？' % (name)):
            self.client.free_dev(name)

        self.query_dev()

    def kick_dev(self, name):
        if self.client_not_connected():
            tkinter.messagebox.showinfo('错误', '未连接服务器')
            return
            
        if tkinter.messagebox.askyesno('提示', '确定强制释放 %s？' % (name)):
            self.client.kick_dev(name)

        self.query_dev()

    def query_dev(self):
        if self.client_not_connected():
            return
        self.query_time = time.time()
        rc, dev_user_list = self.client.query_dev()
        if rc == False:
            return
            
        for dev_user in dev_user_list:
            rc, dev = self.get_dev(dev_user['dev_name'])
            if rc != True:
                continue
            user_list = dev_user['user_list']
            using_user = ''
            if len(user_list):
                using_user = user_list.pop(0)
                dev['using user'].config(text = using_user)
            else:
                dev['using user'].config(text = '')
                
            if len(user_list):
                user_str = ''
                for user in user_list:
                    user_str = user_str + user + '\t'
                    dev['wait user'].config(text = user_str)
            else:
                dev['wait user'].config(text = '')

            if using_user == self.client.user_name:
                if dev['info_msg_box'] == False:
                    dev['info_msg_box'] = True
                    tkinter.messagebox.showinfo('Info', dev['name'] + ' 可以使用了')
            else:
                if dev['info_msg_box'] == True:
                    dev['info_msg_box'] = False

    def status_label_update(self):
        now = time.time()
        if (now - self.query_time) > 60:
            self.query_dev()
        self.status_label.after(1000, self.status_label_update)

if __name__ == '__main__':
    init_window = Tk()
    gui = Client_Gui(init_window)
    gui.set_init_window()
    init_window.mainloop()
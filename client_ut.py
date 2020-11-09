# -*- coding: UTF-8 -*-

import client

def ut1(client):
    valid, ftp_info = client.version_check()
    if valid == True:
        print('No need update...')
    else :
        if ftp_info:
            print('New info:' + str(ftp_info))
            client.download_new_version(ftp_info)
        else :
            print('Invalid & update fail')
                
def ut2(client):
    for i in range(6):
        user_name = "user_%u" % (i)
        client.set_user_name(user_name)
        client.req_dev('dev2')
            
        user_list = client.query_dev()
        print(user_list)
        
    for i in range(6):
        user_name = "user_%u" % (i)
        client.set_user_name(user_name)
        client.free_dev('dev2')
            
        user_list = client.query_dev()
        print(user_list)
              
def ut3(client):
    for i in range(6):
        user_name = "user_%u" % (i)
        client.set_user_name(user_name)
        client.req_dev('dev2')
        
    for i in range(5, 0, -1):
        user_name = "user_%u" % (i)
        client.set_user_name(user_name)
        client.free_dev('dev2')
            
        user_list = client.query_dev()
        print(user_list)
            
def ut4(client):
    for i in range(6):
        user_name = "user_%u" % (i)
        client.set_user_name(user_name)
        client.req_dev('dev2')
        
    for i in range(6):
        client.kick_dev('dev2')
        user_list = client.query_dev()
        print(user_list)


if __name__ == "__main__":
    c = client.Client()
    c.connect('172.0.12.66')
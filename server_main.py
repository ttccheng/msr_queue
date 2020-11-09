# -*- coding: UTF-8 -*-

import server

if __name__ == "__main__":
    serv = server.Server()
    serv.init_dev_list()
    serv.init_connect()
    serv.run()
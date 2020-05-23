#!/usr/bin/env python3

import socket
import sys
import _thread


def client(conn, addr):
    data = conn.recv(4096).decode()
    headers = data.split('\r\n')
    request = headers[0].split(' ')[0]
    port = 80
    host = ""
    for header in headers:
        if header.startswith('Host'):
            hosts = header.split(':')
            if len(hosts) == 3:
                port = int(hosts[2])
            host = hosts[1]
    if request == 'CONNECT':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    else:






if len(sys.argv) != 2:
    print('Wrong number of argument')
    sys.exit()
port = int(sys.argv[1])
ip = socket.gethostbyname('localhost')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, port))
s.listen(5)
try:
    conn, addr = s.accept()
    _thread.start_new_thread(client, (conn, addr))
except KeyboardInterrupt:
    s.close()
    sys.exit()
s.close()
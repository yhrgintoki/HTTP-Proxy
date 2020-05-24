#!/usr/bin/env python3

import socket
import sys
import _thread


def client(client_conn, client_addr):
    data = client_conn.recv(4096).decode()
    headers = data.split('\r\n')
    request = headers[0].split(' ')[0]
    server_port = 80
    # need to change here
    for header in headers:
        if header.lower().startswith('host'):
            hosts = header.split(':')
            if len(hosts) == 3:
                server_port = int(hosts[2])
            server_ip = socket.gethostbyname(hosts[1].strip())
    if request == 'CONNECT':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((server_ip, server_port))
            client_conn.send('HTTP/1.0 200 OK\r\n\r\n'.encode())
        except Exception:
            client_conn.send('HTTP/1.0 502 Bad Gateway\r\n\r\n'.encode())
            sock.close()
            client_conn.close()
            return
        while True:
            request = client_conn.recv(4096)
            if len(request) == 0:
                break
            sock.send(request)
            response = sock.recv(4096)
            client_conn.send(response)
        client_conn.close()
        sock.close()
    else:
        data = data.replace('HTTP/1.1', 'HTTP/1.0', 1)
        data = data.replace('keep-alive', 'close')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))
        sock.send(data)
        response = sock.recv(4096)






if len(sys.argv) != 2:
    print('Wrong number of argument')
    sys.exit()
proxy_port = int(sys.argv[1])
proxy_ip = socket.gethostbyname('localhost')
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.bind((proxy_ip, proxy_port))
proxy_socket.listen(5)
while True:
    try:
        client_conn, client_addr = proxy_socket.accept()
        _thread.start_new_thread(client, (client_conn, client_addr))
    except KeyboardInterrupt:
        proxy_socket.close()
        sys.exit()

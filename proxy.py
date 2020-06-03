#!/usr/bin/env python3

import socket
import sys
import _thread


def client(client_conn, client_addr):
    data = client_conn.recv(4096).decode()
    headers = data.split('\r\n')
    print(headers[0])
    request = headers[0].split(' ')[0]
    server_port = -1
    for header in headers:
        if header.lower().startswith('host'):
            hosts = header.split(':')
            if len(hosts) == 3:
                server_port = int(hosts[2])
            server_ip = socket.gethostbyname(hosts[1].strip())
            break
    if server_port == -1:
        uris = headers[0].split(':')
        if len(uris) == 3:
            port = uris[2].split(' ')
            server_port = int(port[0])
        elif 'https' in headers[0]:
            server_port = 443
        else:
            server_port = 80
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
            while True:
                request = client_conn.recv(1024)
                sock.send(request)
                if len(request) < 1024:
                    break
            if len(request) == 0:
                break
            while True:
                response = sock.recv(1024)
                client_conn.send(response)
                if len(response) < 1024:
                    break
        client_conn.close()
        sock.close()
    else:
        data = data.replace('HTTP/1.1', 'HTTP/1.0', 1)
        data = data.replace('keep-alive', 'close')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))
        sock.send(data)
        while True:
            response = sock.recv(1024)
            if len(response) < 1024:
                break
            client_conn.send(response)
        client_conn.close()
        sock.close()


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

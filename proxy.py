#!/usr/bin/env python3

import socket
import sys
import _thread
import threading

def connect_client_to_server(client_con, server_con):
    while True:
        try:
            request = client_con.recv(1024)
            if len(request) > 0:
                server_con.send(request)
        except socket.error:
            print(str(socket.error))
            print("connect_client_to_server error")
            return


def connect_server_to_client(client_con, server_con):
    while True:
        try:
            response = server_con.recv(1024)
            if len(response) > 0:
                client_con.send(response)
        except socket.error:
            print("connect_server_to_client error")
            return


def client(client_con, client_addr):
    data = ''
    try:
        data = client_con.recv(4096).decode(errors='ignore')
        if not data:
            client_con.close()
            return
    except socket.error:
        print('client error')
        client_con.close()
        return
    headers = data.split('\r\n')
    print(headers[0])
    request = headers[0].split(' ')[0]
    server_port = -1
    server_ip = ''
    for header in headers:
        if header.lower().startswith('host'):
            hosts = header.split(':')
            if len(hosts) == 3:
                server_port = int(hosts[2])
            print("e", hosts[1].strip())
            server_ip = socket.gethostbyname(hosts[1].strip())
            break
    if server_port == -1:
        uris = headers[0].split(':')
        if len(uris) == 3:
            port = uris[2].split(' ')
            server_port = int(port[0])
        elif 'https' in headers[0].lower():
            server_port = 443
        else:
            server_port = 80
    if request == 'CONNECT':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((server_ip, server_port))
            client_con.send('HTTP/1.0 200 OK\r\n\r\n'.encode())
            server_thread = threading.Thread(name=str(client_addr) + '_server', target=connect_server_to_client,
                                             args=(client_con, sock))
            server_thread.setDaemon(True)

            client_thread = threading.Thread(name=str(client_addr) + '_client', target=connect_client_to_server,
                                             args=(client_con, sock))
            client_thread.setDaemon(True)

            server_thread.start()
            client_thread.start()

            server_thread.join()
            client_thread.join()

            sock.close()
            client_con.close()
            #_thread.start_new_thread(connect_client_to_server, (client_conn, sock))
            #_thread.start_new_thread(connect_server_to_client, (client_conn, sock))
        except socket.error:
            client_con.send('HTTP/1.0 502 Bad Gateway\r\n\r\n'.encode())
            sock.close()
            client_con.close()
            return
        client_con.close()
        sock.close()
    else:
        data = data.replace('HTTP/1.1', 'HTTP/1.0', 1)
        data = data.replace('keep-alive', 'close')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("serverip", server_ip)
        print("server_port", server_port)
        sock.connect((server_ip, server_port))
        sock.send(data.encode())
        while True:
            response = sock.recv(1024)
            client_con.send(response)
            if len(response) < 1024:
                break
        client_con.close()
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
        client_thread = threading.Thread(name=str(client_addr), target=client,
                                         args=(client_conn, client_addr))
        client_thread.setDaemon(True)

        # Start the thread
        client_thread.start()
        #_thread.start_new_thread(client, (client_conn, client_addr))
    except KeyboardInterrupt:
        proxy_socket.close()
        sys.exit()

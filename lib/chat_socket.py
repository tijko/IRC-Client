#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno

from socket import error as socket_error
from socket import socket, AF_INET, SOCK_STREAM

from lib import END


class ChatSocket(object):

    def __init__(self, host, port, chat_window):
        self.host = host
        self.port = port
        self.chat_window = chat_window
        self.chat_client_socket = socket(AF_INET, SOCK_STREAM)
        self.chat_client_socket.connect((self.host, self.port))
        self.chat_client_socket.settimeout(3) # XXX connection timesout on bad shutdowns/restarts

    def sendall(self, msg):
        self.msg = msg.encode('utf-8')
        try:
            self.chat_client_socket.sendall(self.msg)
        except socket_error as e:
            self._error_response(e.errno)

    def recvfrom(self, msg_buffer_len):
        try:
            client_response = self.chat_client_socket.recvfrom(4096)
            try:
                decoded_response = client_response[0].decode('utf-8')
            except UnicodeDecodeError:
                return 'Decode error'
            return decoded_response
        except socket_error as e:
            self._error_response(e.errno)

    def close(self):
        try:
            self.chat_client_socket.close()
        except socket_error as e:
            self._error_response(e.errno)

    @property
    def fileno(self):
        return self.chat_client_socket.fileno()

    def _error_response(self, error):
        retry = False
        if error == errno.EPIPE: 
            chat_chat_window_errmsg = 'Error: Broken Pipe'
        elif error == errno.ENOTCONN:
            chat_chat_window_errmsg = 'Error: Transport end not Connected'
        elif error == errno.ETIMEDOUT:
            chat_chat_window_errmsg = 'Error: Connection Timed out...retrying'
            retry = True
        else:
            chat_chat_window_errmsg = 'Error: %d' % error
        self.chat_window._insert('Server', chat_chat_window_errmsg)
        if retry:
            self.sendall(self.msg)


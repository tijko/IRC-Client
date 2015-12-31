#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno

from Tkinter import *
from socket import socket, AF_INET, SOCK_STREAM


class ChatSocket(object):

    def __init__(self, host, port, screen):
        self.host = host
        self.port = port
        self.screen = screen
        self.chat_client_socket = socket(AF_INET, SOCK_STREAM)
        self.chat_client_socket.connect((self.host, self.port))
        self.chat_client_socket.setblocking(0)

    def sendall(self, msg):
        try:
            self.chat_client_socket.sendall(msg)
        except socket.error, err:
            self._error_response(err[0])

    def recvfrom(self, msg_buffer_len):
        try:
            client_response = self.chat_client_socket.recvfrom(4096)
            return client_response[0]
        except socket.error, err:
            self._error_response(err[0])

    def close(self):
        self.chat_client_socket.close()

    @property
    def fileno(self):
        return self.chat_client_socket.fileno()

    def _error_response(self, error):
        if error == errno.EPIPE: 
            chat_screen_errmsg = 'Error: Broken Pipe'
        elif error == errno.ENOTCONN:
            chat_screen_errmsg = 'Error: Transport end not Connected'
        self.screen.insert(END, chat_screen_errmsg)
        self.screen.see(END)


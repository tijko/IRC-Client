#!/usr/bin/env python

import socket
from threading import Thread


class Chat(Thread):

    def __init__(self, conn, channel):
        self.conn = conn
        self.channel = channel
        self.commands = {'whois':self.whois}
        super(Chat, self).__init__()

    def whois(self, query):
        query = 'WHOIS ' + query
        self.conn.sendall(query)

    def run(self):
        while True:
            msg = raw_input('')
            if msg:
                if msg[0] == '/':
                    msg = msg.split()
                    command = self.commands[msg[0][1:].lower()]
                    command(msg[1] + '\r\n')
                else:
                    msg = 'privmsg #%s :'  % self.channel + msg + '\r\n'
                    self.conn.sendall(msg)
                   

class Client(object):
    
    def __init__(self, **kwargs):
        user = kwargs['user']
        port = kwargs['port']
        channel = kwargs['channel']
        self.nick = kwargs['nick']
        self.host = kwargs['host']
        nickdata = 'NICK %s\r\n' % self.nick
        userdata = 'USER %s %s servername :%s\r\n' % (self.nick, self.host, user)
        joindata = 'JOIN #%s\r\n' % channel
        self.namedata = 'NAMES #%s\r\n' % channel

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, port))

        self.client.sendall(nickdata)
        self.client.sendall(userdata)
        self.client.sendall(joindata)
        self.client.sendall(self.namedata)

        Thread.start(Chat(self.client, channel))
        self.conn = None
        while True:
            self.data = self.client.recvfrom(1024)
            if self.data:
                self.recv_msg = tuple(self.data[0].split())
                if self.recv_msg[0] == 'PING':
                    self.client.sendall('PONG ' + self.recv_msg[1] + '\r\n')
                    print 'sent pong'
                else: 
                    self.msg_handle()                    
        
    def msg_handle(self, join='', userlist=None):
        user, cmd, channel = self.recv_msg[:3]
        back = self.recv_msg[3:]
        user = user.split('!')[:1]
        if user[0][1:].endswith('.freenode.net') and not self.conn:
            print 'SUCCESSFULLY CONNECTED TO %s' % self.host
            self.conn = 1
        else:
            print '%s | %s' % (user[0][1:], ' '.join([i for i in back])[1:-2])
        if channel == self.nick and user[0][1:] in join:     
            self.client.sendall(('PRIVMSG %s :keep it in the open' % 
                                  user[0][1:]) + '\r\n')
        if cmd == 'JOIN':
            if not userlist:
                self.client.sendall(self.namedata)
                userlist = 1
                print 'SUCCESFULLY JOINED %s' % channel


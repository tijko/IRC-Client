#!/usr/bin/env python

import socket
import time
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
                    try:
                        command = self.commands[msg[0][1:].lower()]
                        command(msg[1] + '\r\n')
                    except KeyError:
                        print 'Server | Unknown Command!'
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
        try:
            self.client.connect((self.host, port))
        except socket.error:
            print 'Connection Failed! --> check host & port'
            return
        self.client.sendall(nickdata)
        self.client.sendall(userdata)
        self.client.sendall(joindata)
        self.client.sendall(self.namedata)

        Thread.start(Chat(self.client, channel))
        self.conn = None

        self.server_reply = {'311':self.whois_user, '319':self.whois_chan}

        while True:
            self.data = self.client.recvfrom(1024)
            if self.data:
                self.recv_msg = tuple(self.data[0].split())
                if self.recv_msg[0] == 'PING':
                    self.client.sendall('PONG ' + self.recv_msg[1] + '\r\n')
                    print 'Channel Ping @ ==> %s' % time.ctime()
                else: 
                    if len(self.recv_msg) >= 3:
                        self.msg_handle()                    

    def whois_user(self, user_data):
        server_repl = 'User: %s' % (user_data[1] + '@' + user_data[2])
        print server_repl

    def whois_chan(self, chan_data):
        server_repl = 'Real Name: %s \nServer: %s' % (chan_data[0], chan_data[2].strip(':')) 
        print server_repl
        
    def msg_handle(self, join='', userlist=None):
        user, cmd, channel = self.recv_msg[:3]  
        back = self.recv_msg[3:]
        user = user.split('!')[0].strip(':')
        if user.endswith('.freenode.net') and not self.conn:
            print '\nSUCCESSFULLY CONNECTED TO %s' % self.host
            self.server = user
            self.conn = 1
        elif user.endswith('.freenode.net') and self.conn:
            try:
                reply = self.server_reply[cmd]
                reply(back)
            except KeyError:
                pass 
        if cmd == 'PRIVMSG':
            print '%s | %s' % (user, ' '.join(i for i in back).strip(':')) 
        if cmd == 'JOIN':
            if not userlist:
                self.client.sendall(self.namedata)
                userlist = 1
                print 'SUCCESFULLY JOINED %s\n' % channel


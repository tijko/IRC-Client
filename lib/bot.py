#!/usr/bin/env python

#'irc.freenode.net', 6667
# make a.i. to do response -- markov-chain
# reconnect on time out?
# handle nick in use ... ??? 

import socket
from threading import Thread

class Chat(Thread):

    def __init__(self, conn, channel):
        self.conn = conn
        self.channel = channel
        super(Chat, self).__init__()

    def run(self):
        while True:
            msg = raw_input('')
            if msg:
                # check for commands
                if msg[0] == '/':
                    pass
                else:
                    msg = 'privmsg #%s :'  % self.channel + msg + '\r\n'
                    self.conn.sendall(msg)

# most of the IRC-commands work --> 'ME'? 
class Client(object):
    
    def __init__(self, **kwargs):
        user = kwargs['user']
        port = kwargs['port']
        channel = kwargs['channel']
        self.nick = kwargs['nick']
        self.host = kwargs['host']
        nickdata = 'NICK %s\r\n' % self.nick
        userdata = 'USER %s %s bla :%s\r\n' % (self.nick, self.host, user)
        joindata = 'JOIN #%s\r\n' % channel
        self.namedata = 'NAMES #%s\r\n' % channel

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        self.client.sendall(nickdata)
        self.client.sendall(userdata)
        self.client.sendall(joindata)
        self.client.sendall(self.namedata)

        Thread.start(Chat(self.client, channel))
        while True:
            self.data = self.client.recvfrom(1024)
            if self.data:
                self.recv_msg = tuple(self.data[0].split(' '))
                if len(self.recv_msg) > 2:
                    self.msg_handle()                    
        
    def msg_handle(self, join='', userlist=None):
        user, cmd, channel = self.recv_msg[:3]
        back = self.recv_msg[3:]
        user = user.split('!')[:1]
        if user[0][1:].endswith('.freenode.net'):
            print 'SUCCESSFULLY CONNECTED TO %s' % self.host
            pass
        else:
            print '%s | %s' % (user[0][1:], ' '.join([i for i in back])[1:-2])
#        print 'COMMAND == %s' % cmd
#        print 'CHANNEL == %s' % channel
        # check if Bot msg'd itself --> infinite loop
        if channel == self.nick and user[0][1:] in join:     
            self.client.sendall(('PRIVMSG %s :keep it in the open' % 
                                  user[0][1:]) + '\r\n')
        if cmd == 'JOIN':
            if not userlist:
                self.client.sendall(self.namedata)
                join = self.client.recvfrom(1024)
                join = str(join).split(':')
                join = join[2]
                join = join.split(' ')
                join = join[:-1]
                userlist = 1
                print 'SUCCESFULLY JOINED %s' % channel


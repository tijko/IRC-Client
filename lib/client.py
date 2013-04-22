#!/usr/bin/env python

import socket
import time
from threading import Thread


class Chat(Thread):

    def __init__(self, conn, channel):
        self.conn = conn
        self.channel = channel
        self.commands = {'names':self._names, 'whois':self._whois, 'help':self._help}
        super(Chat, self).__init__()

    def _names(self, chan):
        '''Usage: /NAMES [<channel>] --> List all nicks visible on channel''' 
        query = 'NAMES %s' % chan
        self.conn.sendall(query)

    def _whois(self, query):
        '''Usage: /WHOIS [<server>] <nickmask> --> Query information about a user.'''
        query = 'WHOIS ' + query
        self.conn.sendall(query)

    def _help(self, cmd=None):
        '''Usage: /HELP [<command>] --> Show help information for/on valid commands'''
        if not cmd:
            print 'Commands:' 
            all_commands = '< '
            for c in self.commands.keys():
                all_commands += (c.upper() + '  ')
            all_commands += '>\n'
            print all_commands
        else:
            try:
                func_info = cmd.lower() 
                print self.commands[func_info].__doc__
            except KeyError:
                print 'Server | Unknown Command!'
                print 'Type /HELP for list of commands\n'

    def run(self):
        while True:
            msg = raw_input('')
            if msg:
                if msg[0] == '/':
                    msg = msg.split()
                    try:
                        command = self.commands[msg[0][1:].lower()]
                        if msg[0][1:].lower() == 'help':
                            if len(msg) > 1:
                                command(msg[1])
                            else:
                                command()
                        elif len(msg) < 2:
                            print command.func_doc
                        else:
                            command(msg[1] + '\r\n')
                    except KeyError:
                        print 'Server | Unknown Command!'
                        print 'Type /HELP for list of commands'
                        print 'or /HELP <command> for information on a valid command\n'
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

        self.server_reply = {'311':self.whois_user_repl, '319':self.whois_chan_repl, 
                             '353':self.names_repl}

        while True:
            self.data = self.client.recvfrom(1024)
            if self.data:
                self.recv_msg = tuple(self.data[0].split())
                if self.recv_msg[0] == 'PING':
                    self.client.sendall('PONG ' + self.recv_msg[1] + '\r\n')
                    print 'Channel Ping@ ==> %s' % time.ctime()
                else: 
                    if len(self.recv_msg) >= 3:
                        self.msg_handle()                    

    def whois_user_repl(self, user_data):
        server_repl = 'User: %s' % (user_data[1] + '@' + user_data[2])
        print server_repl 

    def whois_chan_repl(self, chan_data):
        server_repl = 'Real Name: %s \nServer: %s' % (chan_data[0], chan_data[2].strip(':')) 
        print server_repl + '\n'
    
    def names_repl(self, userlist):
        if any(i.endswith('.freenode.net') for i in userlist[2:]):
            pass
        else:
            server_repl = ('Users available on %s:\n' + '=' * 25 + '\n') % userlist[1]
            for usr in userlist[2:]:
                server_repl += ('  ~' + usr.strip(':@') + '\n')
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


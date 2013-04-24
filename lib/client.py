# --*-- coding: utf-8 --*--
#!/usr/bin/env python

import socket
import time
from threading import Thread


class Chat(Thread):

    def __init__(self, conn, server, channel):
        self.conn = conn
        self.server = server
        self.channel = channel
        self.commands = {'names':self._names, 'whois':self._whois, 
                         'info':self._info, 'help':self._help,
                         'links':self._links}
        super(Chat, self).__init__()

    def _names(self, chan):
        '''Usage: /NAMES [<channel>] --> List all nicks visible on channel.''' 
        query = 'NAMES %s' % chan
        self.conn.sendall(query)

    def _whois(self, query):
        '''Usage: /WHOIS [<server>] <nickmask> --> Query information about a user.'''
        query = 'WHOIS ' + query
        self.conn.sendall(query)

    def _info(self, srv=None):
        '''Usage: /INFO (optional [<server>]) --> Returns information that describes the server, optional parameter defaults to current server.'''
        if srv is None:
            query = 'INFO %s' % (self.server + '\r\n')
            self.conn.sendall(query)
        else:
            query = 'INFO %s' % (srv + '\r\n')
            self.conn.sendall(query)

    def _links(self, srv=None):
        '''Usage: /LINKS --> Lists all of the servers currently linked to network'''
        if srv is None:
            query = 'LINKS \r\n'
            self.conn.sendall(query)
        else:
            query = 'LINKS %s\r\n' % srv
            self.conn.sendall(query)

    def _help(self, cmd=None):
        '''Usage: /HELP [<command>] --> Show help information for/on valid commands.'''
        if not cmd:
            print 'Commands:' 
            all_commands = '< '
            for c in self.commands.keys():
                all_commands += (c.upper() + '  ')
            all_commands += '>\n'
            print all_commands
        else:
            try:
                cmd = cmd.strip('\r\n') 
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
                    msg_cmd = msg[0][1:].lower()
                    command = self.commands.get(msg_cmd)
                    if command:
                        if (msg_cmd == 'help' or msg_cmd == 'info' or 
                            msg_cmd == 'links'):
                            msg.append(None)
                            command(msg[1])
                        elif len(msg) < 2:
                            print command.func_doc
                        else:
                            command(msg[1] + '\r\n')
                    else:
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
        self.channel = kwargs['channel']
        self.nick = kwargs['nick']
        self.host = kwargs['host']
        nickdata = 'NICK %s\r\n' % self.nick
        userdata = 'USER %s %s servername :%s\r\n' % (self.nick, self.host, user)
        joindata = 'JOIN #%s\r\n' % self.channel
        self.namedata = 'NAMES #%s\r\n' % self.channel

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
        self.conn = None

        self.joined_chan = False
        self.server_reply = {'311':self.whois_user_repl, '319':self.whois_chan_repl, 
                             '353':self.names_repl,      '371':self.info_repl,
                             '364':self.links_repl}

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
        server_repl = ('Real Name: %s \nServer: %s' % 
                      (chan_data[0], chan_data[2].strip(':'))) 
        print server_repl + '\n'
    
    def names_repl(self, userlist):
        if any(i.endswith('.freenode.net') for i in userlist[2:]):
            pass
        else:
            server_repl = ('Users available on %s:\n' + '=' * 25 + '\n') % userlist[1]
            for usr in userlist[2:]:
                server_repl += ('  ~' + usr.strip(':@') + '\n')
            print server_repl 
    
    def info_repl(self, server_data):
        skips = [self.server, self.nick, ':', '371', (':' + self.server)]
        if len(server_data) > 2:
            server_data = ' '.join(i for i in server_data if i not in skips).split(' :')
            for i in server_data:
                if '.freenode.net' in i and i[:3] != 'irc':
                    pass
                elif len(i) > 1:
                    print i.strip(':')         
            print '\n'

    def links_repl(self, server_data):
        link_info = ' '.join(i.strip(':') for i in server_data[2:6])
        if int(link_info[0]) < 1:
            link_info = link_info[2:]
        else:
            link_info = 'HOPS: ' + link_info
        if '365' in server_data:
            print link_info + '\n'
            return
        print link_info

    def msg_handle(self, join='', userlist=None):
        user, cmd, channel = self.recv_msg[:3]  
        back = self.recv_msg[3:]
        user = user.split('!')[0].strip(':')
        if user.endswith('.freenode.net') and not self.conn:
            print '\nSUCCESSFULLY CONNECTED TO %s' % self.host
            self.server = user
            Thread.start(Chat(self.client, self.server, self.channel))
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
            if not self.joined_chan: 
                self.client.sendall(self.namedata)
                self.joined_chan = True
                print 'SUCCESFULLY JOINED %s\n' % channel
            else:
                print '%s | entered --> %s' % (user, channel)
        if cmd == 'QUIT':
            print '%s | left --> %s' % (user, '#' + self.channel)


#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import socket
import time
from threading import Thread
from chk_wiki import wiki_lookup


class Chat(Thread):

    def __init__(self, **kwargs):
        self.conn = kwargs['conn']
        self.server = kwargs['server']
        self.channel = kwargs['channel']
        self.nick = kwargs['nick']
        self.commands = {'names':self._names, 
                         'whois':self._whois, 
                         'info':self._info, 
                         'help':self._help,
                         'links':self._links, 
                         'stats':self._stats,
                         'quit':self._quit,
                         'part':self._part,
                         'join':self._join,
                         'noise':self._noise,
                         'block':self._block,
                         'unblock':self._unblock,
                         'topic':self._topic,
                         'version':self._version,
                         'whereami':self._whereami,
                         'blocklist':self._blocklist,
                         'nick':self._nick,
                         'whowas':self._whowas,
                         'whatis':self._whatis,
                         'whoami':self._whoami
                        }

        super(Chat, self).__init__()
        self.CHATTING = True
        self.verbose = True
        self.blocked = kwargs['blocked']

    def _names(self, chan=None):
        '''Usage: /NAMES <channel> --> 

           List all nicks visible on channel.
        ''' 
        if not chan:
            print self._names.__doc__
            return
        query = 'NAMES %s\r\n' % chan
        self.conn.sendall(query)

    def _whois(self, query=None):
        '''Usage: /WHOIS <nick> --> 

           Query information about a user.
        '''
        if not query:
            print self._whois.__doc__
            return
        query = 'WHOIS %s\r\n' % query
        self.conn.sendall(query)

    def _info(self, srv=None):
        '''Usage: /INFO (optional <server> --> 

           Returns information that describes the server, 

           optional parameter defaults to current server.
        '''
        if srv is None:
            query = 'INFO %s\r\n' % self.server
            self.conn.sendall(query)
        else:
            query = 'INFO %s\r\n' % srv
            self.conn.sendall(query)

    def _links(self, srv=None):
        '''Usage: /LINKS --> 

           Lists all of the servers currently linked to network.
        '''
        if srv is None:
            query = 'LINKS \r\n'
            self.conn.sendall(query)
        else:
            query = 'LINKS %s\r\n' % srv
            self.conn.sendall(query)

    def _stats(self, flags=None):
        '''Usage: /STATS <flag> -->

           Shows statistical information on the server.

           ## STAT-FLAGS ##:

               I = Lists all the current I:Lines (Client auth Lines)

               u = Server Uptime

               m = Gives the Server command list

               L = Information about current server connections
        '''
        if not flags:
            print self._stats.__doc__
            return
        query = 'STATS %s %s\r\n' % (flags, self.server)
        self.conn.sendall(query)

    def _quit(self, msg=None):
        '''Usage: /QUIT (optional <message>) -->

           Ends a client session from server.
        '''
        self.CHATTING = False
        q_signal = 'QUIT %s\r\n'
        self.conn.sendall(q_signal) 

    def _join(self, chan=None):
        '''Usage: /JOIN <channel> -->

           Allows a client to start listening on the specified channel
        '''
        if not chan:
            print self._join.__doc__
            return
        self._part('#' + self.channel)
        chan_join = 'JOIN %s\r\n' % chan
        self.conn.sendall(chan_join)
        self.channel = chan.strip('#')

    def _part(self, chan=None):
        '''Usage: /PART <channel> -->

           Leave a channels active user's list.
        '''
        if not chan:
            print self._part.__doc__
            return
        chan_part = 'PART %s\r\n' % chan
        self.conn.sendall(chan_part)

    def _noise(self, flags=None):
        '''Usage: /NOISE <flag> -->

           Show or block the extra info for the current channel.

           ## NOISE-FLAGS ##:
        
               s = show all channel info

               b = block all channel info
        '''                                              
        if not flags:
            print self._noise.__doc__
            return
        elif flags == 's':
            self.verbose = True
        elif flags == 'b':
            self.verbose = False

    def _block(self, nick=None): 
        '''Usage: /BLOCK <nick> --> 
           
           Blocks the chat from the nick supplied.
        '''
        if not nick:
            print self._block.__doc__
            return
        if nick not in self.blocked:
            self.blocked.append(nick)

    def _unblock(self, nick=None):
        '''Usage: /UNBLOCK <nick> -->

           Unblocks chat from a nick thats currently being blocked.
        '''
        if not nick:
            print self._unblock.__doc__
            return
        if nick in self.blocked:
            self.blocked.remove(nick)   

    def _topic(self, chan=None):
        '''Usage: /TOPIC <channel> --> 

           Prints ou the topic for the supplied channel.
        '''
        if not chan:
            print self._topic.__doc__
            return
        topic = 'TOPIC %s\r\n' % chan
        self.conn.sendall(topic)

    def _version(self, server=None):
        '''Usage: /VERSION <server> -->

           Returns the version of program that the server is using.
        '''
        if not server:
            print self._version.__doc__
            return
        ver_chk = 'VERSION %s\r\n' % server
        self.conn.sendall(ver_chk)

    def _whereami(self, query=None):
        '''Usage: /WHEREAMI -->

           This command will let you know which channel and server you are

           currently connected to.
        '''
        if not query:
            print '\nYou are currently connected to server <%s> and in channel <%s>\n' % (self.server, self.channel)

    def _blocklist(self, nick=None):
        '''Usage: /BLOCKLIST -->

           Shows all the nicks currently being blocked.
        '''
        if not nick:
            print 'Blocked Nicks: %s' % str(self.blocked)

    def _nick(self, nick=None):
        '''Usage /NICK <nick> -->

           Registers the supplied nick with services.
        '''
        if not nick:
            print self._nick.__doc__
            return
        self.nick = nick
        ident = "NICK %s\r\n" % self.nick
        self.conn.sendall(ident)
        self._join('#' + self.channel)

    def _whowas(self, nick=None):
        '''Usage: /WHOWAS <nick> -->

           Returns information about a nick that doesn't exist anymore.
        '''
        if not nick:
            print self._whowas.__doc__
            return
        whowas_msg = "WHOWAS %s\r\n" % nick
        self.conn.sendall(whowas_msg)

    def _whatis(self, lookup=None):
        '''Usage: /WHATIS <item> -->

           Returns a query of wikipedia for the supplied item.
        '''
        if not lookup:
            print self._whatis__doc__
            return
        wiki_lookup(lookup)        

    def _whoami(self, nick=None):
        '''Usage: /WHOAMI -->
    
           Prints out your current nick.
        '''
        if nick:
            print self._whoami.__doc__
            return
        print "You are currently known as => %s" % self.nick

    def _help(self, cmd=None):
        '''Usage: /HELP (optional <command>) --> 

           Show help information for/on valid commands.
        '''
        if not cmd:
            print 'Commands:\n\n<<<' + ' - '.join(self.commands.keys()) + '>>>\n'
            return
        try:
            func_info = cmd.lower() 
            print self.commands[func_info].__doc__
        except KeyError:
            print 'Server | Unknown Command!'
            print 'Type /HELP for list of commands\n'

    def run(self):
        while self.CHATTING:
            msg = raw_input('')
            if msg:
                if msg[0] == '/':
                    msg = msg.split() + [None]
                    msg_cmd = msg[0][1:].lower()
                    command = self.commands.get(msg_cmd)
                    if command:
                        command(msg[1])
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
        password = kwargs['password']
        self.channel = kwargs['channel']
        self.nick = kwargs['nick']
        self.host = kwargs['host']
        userdata = 'USER %s %s servername :%s\r\n' % (self.nick, self.host, user)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.host, port))
        except socket.error:
            print 'Connection Failed! --> check host & port'
            return
        if password:
            self.client.sendall('PASS %s\r\n' % password)
        self.client.sendall('NICK %s\r\n' % self.nick)
        self.client.sendall(userdata)
        self.client.sendall('JOIN #%s\r\n' % self.channel)
        self.client.sendall('NAMES #%s\r\n' % self.channel)
        self.conn = None

        self.blocked = list()
        self.CHATTING = True
        self.server_reply = {'311':self.whois_user_repl, 
                             '319':self.whois_chan_repl, 
                             '353':self.names_repl,      
                             '371':self.info_repl,
                             '364':self.links_repl,

                             '481':self.perm_denied_repl,
                             '263':self.rate_lim_repl,
                             '212':self.server_com_repl,
                             '211':self.server_con_repl,
                             '242':self.server_utme_repl,
                             '250':self.server_utme_repl,
                             '215':self.clnt_auth_repl,
                             '351':self.server_ver,
                             '005':self.server_aux,
                             '331':self.chan_topic,
                             '332':self.chan_topic,
                             '433':self.nick_inuse,
                             '314':self.whois_user_repl,
                             '330':self.whowas_repl
                            }

        while self.CHATTING:
            try:
                self.data = self.client.recvfrom(1024)
            except socket.error:
                print "Bad Connection!"
                return
            if self.data and len(self.data[0]) > 0:
                self.recv_msg = tuple(self.data[0].split())
                if self.recv_msg[0] == 'PING':
                    self.client.sendall('PONG ' + self.recv_msg[1] + '\r\n')
                    print 'Channel Ping@ ==> %s' % time.ctime()
                else: 
                    if len(self.recv_msg) >= 3:
                        self.msg_handle()       
            elif self.data and len(self.data[0]) == 0:
                print 'Connection Dropped!'
                return

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

    def perm_denied_repl(self, server_response):
        server_response = ' '.join(server_response).strip(':')
        print server_response + '\n'

    def rate_lim_repl(self, server_response):
        server_response = ' '.join(server_response[1:]).strip(':')
        print server_response + '\n'
    
    def server_com_repl(self, server_coms):
        skips = [self.nick, ':' + self.server]
        for com in [i for i in server_coms if i not in skips]:
            if not com.strip(':').isdigit():
                print '    > %s' % com
        print ''
            
    def server_con_repl(self, server_connections):
        server_connections = ' '.join(server_connections)
        print server_connections + '\n' 

    def server_utme_repl(self, server_data):
        server_data = ' '.join(server_data[:9]).strip(':')
        print server_data + '\n'

    def clnt_auth_repl(self, client_data):
        client_data = ' '.join(client_data)
        print client_data + '\n'

    def server_ver(self, server_data):
        print '\nServer Version: %s\n' % server_data[0]

    def server_aux(self, server_data):
        print ' '.join(server_data) + '\n'

    def chan_topic(self, topic):
        print '\n' + 'Topic for %s' % (' '.join(topic)) + '\n'

    def nick_inuse(self, msg):
        print '\n' + ' '.join(msg[:6])
        print 'Use the /NICK <nick> command to choose a new nick' 

    def whowas_repl(self, server_data):
        skips = [self.nick, ':' + self.server, '330', '369', '312', '314']
        whowas_msg = ' '.join(i for i in server_data[:-3] if i not in skips)
        pos = 0
        msg = whowas_msg.split(' :')
        while pos < len(msg):
            out = ('\n' + msg[pos].split()[0] + 
                   ' ' + ''.join(msg[pos + 1]) +  
                   ' ' + ''.join(msg[pos + 2]))
            pos += 3
            print out
    
    def msg_handle(self, join='', userlist=None):
        user, cmd, channel = self.recv_msg[:3]  
        back = self.recv_msg[3:]
        user = user.split('!')[0].strip(':')
        if user.endswith('.freenode.net') and not self.conn:
            print '\nSUCCESSFULLY CONNECTED TO %s' % self.host
            self.server = user
            self.chat = Chat(conn=self.client, 
                             server=self.server, 
                             channel=self.channel,
                             nick = self.nick, 
                             blocked= self.blocked)
            Thread.start(self.chat)    
            self.conn = 1
        elif user.endswith('.freenode.net') and self.conn:
            try:
                self.nick = channel 
                reply = self.server_reply[cmd]
                reply(back)
            except KeyError:
                pass 
        if cmd == 'PRIVMSG' and user not in self.blocked:
            print '%s | %s' % (user, ' '.join(i for i in back).strip(':')) 
        if cmd == 'JOIN':
            if user == self.nick:
                namedata = 'NAMES #%s\r\n' % channel
                self.client.sendall(namedata)
                self.channel = channel
                print 'SUCCESFULLY JOINED %s\n' % channel
            elif user != self.nick and self.chat.verbose:
                self.channel = channel
                print '%s | entered --> %s' % (user, channel)
        if cmd == 'QUIT':
            if user == self.nick:
                self.CHATTING = False                
            elif user != self.nick and self.chat.verbose:
                print '%s | left --> %s' % (user, '#' + self.channel)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import os
import select
import subprocess

from .chk_wiki import Wiki
from .responses import Response
from .chat_socket import ChatSocket
 
from lib import Entry, Scrollbar, Text, TclError, WORD,\
                NORMAL, DISABLED, CURRENT, END, N, S, E, W

try:
    from Queue import Queue
except ImportError:
    from queue import Queue


class Client(object):
    
    def __init__(self, **kwargs):
        self.root = kwargs['root']
        self.user = kwargs['user']
        self.port = kwargs['port']
        self.password = kwargs['password']
        self.channel = kwargs['channel'] 
        self.nick = kwargs['nick']
        self.host = kwargs['host']
        self.create_window
        self.client = ChatSocket(self.host, self.port, self.chat_window)
        self.server_login
        self.conn = False                                 
        self.paused = False 
        self.logging = False
        self.search = False
        self.verbose = True
        self.blocked = list()
        self.ln_strip = lambda s: s.strip(':')
        self.rspd = Response(self.chat_window, self.nick) 
        self.server_reply = {'311':self.rspd.whois_user_repl,  
                             '319':self.rspd.whois_chan_repl, 
                             '353':self.rspd.names_repl,      
                             '371':self.rspd.info_repl,
                             '364':self.rspd.links_repl,
                             '481':self.rspd.perm_denied_repl,
                             '263':self.rspd.rate_lim_repl,
                             '212':self.rspd.server_com_repl,
                             '211':self.rspd.server_con_repl,
                             '242':self.rspd.server_utme_repl,
                             '250':self.rspd.server_utme_repl,
                             '215':self.rspd.clnt_auth_repl,
                             '351':self.rspd.server_ver,
                             '005':self.rspd.server_aux,
                             '331':self.rspd.chan_topic,
                             '332':self.rspd.chan_topic,
                             '433':self.rspd.nick_inuse,
                             '314':self.rspd.whois_user_repl,
                             '322':self.rspd.list_repl,
                             '219':self.rspd.server_com_end,
                             '366':self.rspd.end_names_repl
                            }

        self.commands = {'names':self._names, 
                         'whois':self._whois, 
                         'info':self._info, 
                         'help':self._help,
                         'links':self._links, 
                         'stats':self._stats,
                         'quit':self._quit,
                         'part':self._part,
                         'join':self._join,
                         'wjoin':self._wjoin,
                         'suser':self._shared,
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
                         'whoami':self._whoami,
                         'list':self._list,
                         'pause':self._pause,
                         'reconnect':self._reconnect,
                         'msg':self._usermsg,
                         'log':self._log
                        }

    def _names(self, chan=None):
        '''
           Usage: /NAMES <channel> --> List all nicks visible on channel.
        ''' 
        if chan is None: return self.command_error(self._names.__doc__)
        query = 'NAMES {}\r\n'.format(chan)
        self.cmd_names = True
        self.client.sendall(query)

    def _shared(self, chan1=None, chan2=None):
        '''
            Usage: /SUSER <channel 1> <channel 2> --> List all nicks in both channels.
        '''
        if not all([chan1, chan2]):
            return self.command_error(self._shared.__doc__)
        self.rspd.comp_chan_names = True
        query = 'NAMES {}\r\n'.format(chan1)
        self.client.sendall(query)
        query = 'NAMES {}\r\n'.format(chan2)
        self.client.sendall(query)

    def _whois(self, query=None):
        '''
           Usage: /WHOIS <nick> --> Query information about a user.
        '''
        if query is None:
            return self.command_error(self._whois.__doc__)
        query = 'WHOIS {}\r\n'.format(query)
        self.client.sendall(query)

    def _info(self, srv=None):
        '''
           Usage: /INFO (optional <server> --> Returns information that describes the server, 

           optional parameter defaults to current server.
        '''
        if srv is None:
            query = 'INFO {}\r\n'.format(self.server)
        else:
            query = 'INFO {}\r\n'.format(srv)
        self.client.sendall(query)

    def _links(self, srv=None):
        '''
           Usage: /LINKS --> Lists all of the servers currently linked to network.
        '''
        if srv is None:
            query = 'LINKS \r\n'
        else:
            query = 'LINKS {}\r\n'.format(srv)
        self.client.sendall(query)

    def _stats(self, flags=None):
        '''
           Usage: /STATS <flag> --> Shows statistical information on the server.

           ## STAT-FLAGS ##:

               I = Lists all the current I:Lines (Client auth Lines)

               u = Server Uptime

               m = Gives the Server command list

               L = Information about current server connections
        '''
        if not flags: # XXX check range
            return self.command_error(self._stats.__doc__)
        query = 'STATS {} {}\r\n'.format(flags, self.server)
        self.client.sendall(query)

    def _quit(self, msg=None):
        '''
           Usage: /QUIT (optional <message>) --> Ends a client session from server.
        '''
        q_signal = 'QUIT %s\r\n' # XXX set to None if msg is None?
        self.client.sendall(q_signal) 
        self.client.close()
        if self.logging:
            self.log_file.close()
        self.root.destroy()

    def _join(self, chan=None):
        '''
           Usage: /JOIN <channel> --> Allows a client to start communicating on the specified channel
        '''
        if chan is None:
            return self.command_error(self._join.__doc__)
        if isinstance(self.channel, list):
            for channel in self.channel:
                self._part(channel)
        else: 
            self._part(self.channel)
        self.conn = False
        chan_join = 'JOIN {}\r\n'.format(chan)
        self.client.sendall(chan_join)
        self.channel = chan.strip('#')

    def _wjoin(self, chan=None):
        '''
            Usage: /WJOIN <channel> --> Allows a client to start communicating simultaneously on the specified channel and the current channel/s
        '''
        if chan is None or not self.channel:
            return self.command_error(self._wjoin.__doc__)
        self.channel = [self.channel, chan]
        chan_join = 'JOIN {}\r\n'.format(chan)
        self.client.sendall(chan_join)            

    def _part(self, chan=None):
        '''
           Usage: /PART <channel> --> Leave a channels active user's list.
        '''
        if chan is None:
            return self.command_error(self._part.__doc__)
        if isinstance(self.channel, str) and chan == self.channel: 
            self.channel = None
            chan_part = 'PART {}\r\n'.format(chan)
            self.client.sendall(chan_part)
        elif isinstance(self.channel, list) and chan in self.channel:
            self.channel.remove(chan)
            chan_part = 'PART {}\r\n'.format(chan)
            self.client.sendall(chan_part)
            if not self.channel:
                self.channel = None
        else:
            self.chat_window._insert('Server', 'You are not currently in {}\n'.format(chan))

    def _noise(self, flags=None):
        '''
           Usage: /NOISE <flag> --> Show or block the extra info for the current channel.

           ## NOISE-FLAGS ##:
        
               s = show all channel info

               b = block all channel info
        '''                                              
        if flags is None:
            return self.command_error(self._noise.__doc__)
        elif flags == 's':
            self.verbose = True
        elif flags == 'b':
            self.verbose = False

    def _block(self, nick=None): 
        '''
           Usage: /BLOCK <nick> --> Blocks the chat from the nick supplied.
        '''
        if nick is None:
            return self.command_error(self._block.__doc__)
        if nick not in self.blocked:
            self.blocked.append(nick)

    def _unblock(self, nick=None):
        '''
           Usage: /UNBLOCK <nick> --> Unblocks chat from a nick thats currently being blocked.
        '''
        if nick is None:
            return self.command_error(self._unblock.__doc__)
        if nick in self.blocked:
            self.blocked.remove(nick)   

    def _topic(self, chan=None):
        '''
           Usage: /TOPIC <channel> --> Prints out the topic for the supplied channel.
        '''
        if chan is None:
            return self.command_error(self._topic.__doc__)
        topic = 'TOPIC {}\r\n'.format(chan)
        self.client.sendall(topic)

    def _version(self, server=None):
        '''
           Usage: /VERSION <server> --> Returns the version of program that the server is using.
        '''
        if server is None:
            return self.command_error(self._version.__doc__)
        ver_chk = 'VERSION {}\r\n'.format(server)
        self.cmd_ver = True
        self.client.sendall(ver_chk)

    def _whereami(self, query=None):
        '''
           Usage: /WHEREAMI --> This command will let you know which channel and server you are

           currently connected to.
        '''
        if query is None:
            self.chat_window._insert('Server', 'You are currently connected to server\
                                      <{}> and in channel <{}>\n'.format(
                                      self.server, self.channel)) 

    def _blocklist(self, nick=None):
        '''
           Usage: /BLOCKLIST --> Shows all the nicks currently being blocked.
        '''
        if nick is None:
            self.chat_window._insert('Server', 'Blocked Nicks: {}\n'.format(self.blocked))

    def _nick(self, nick=None):
        '''
           Usage /NICK <nick> --> Registers the supplied nick with services.
        '''
        if nick is None:
            return self.command_error(self._nick.__doc__)
        self.nick = nick
        self.rspd.nick = nick
        ident = 'NICK {}\r\n'.format(self.nick)
        self.client.sendall(ident)
        if self.channel: 
            self._join(self.channel)

    def _whowas(self, nick=None):
        '''
           Usage: /WHOWAS <nick> --> Returns information about a nick that doesn't exist anymore.
        '''
        if nick is None:
            return self.command_error(self._whowas.__doc__)
        whowas_msg = 'WHOWAS {}\r\n'.format(nick)
        self.client.sendall(whowas_msg)

    def _whatis(self, lookup=None):
        '''
           Usage: /WHATIS <item> --> Returns a query of wikipedia for the supplied item.
        '''
        if lookup is None:
            return self.command_error(self._whatis.__doc__)
        if not self.search:        
            self.wiki_q = Queue()
            self.wiki = Wiki(self, self.chat_window, lookup, self.wiki_q)
            self.wiki.start()
            self.search = True
        elif lookup.lower() == 'y':
            self.wiki_q.put('y')
        elif lookup.lower() == 'n':
            self.wiki_q.put('n')
            self.search = False
        elif lookup.isdigit():
            self.wiki_q.put(lookup)

    def _whoami(self, nick=None):
        '''
           Usage: /WHOAMI --> Prints out your current nick.
        '''
        if nick is not None:
            return self.command_error(self._whoami.__doc__)
        self.chat_window._insert('Server', 'You are currently known as => {}\n'.format(
                                                                    self.nick))

    def _list(self, log=None):
        '''
           Usage: /LIST (optional <log>) --> Will show all the channels\
                                             available and their topic.
        '''
        if log is None:
            lst_msg = 'LIST\r\n'
            self.client.sendall(lst_msg)
        elif log == 'l':
            lst_msg = 'LIST\r\n'
            self.client.sendall(lst_msg)
            self.rspd.log_links = True

    def _help(self, cmd=None):
        '''
           Usage: /HELP (optional <command>) --> Show help information\
                                                 for/on valid commands.
        '''
        if cmd is None:
            new_msg = 'Commands <<{}>>\n'.format(' - '.join(self.commands.keys()))
            self.chat_window._insert('Server', new_msg)
            return
        try:
            func_info = cmd.lower() 
            self.command_error(self.commands[func_info].__doc__)
        except KeyError:
            new_msg = 'Unknown Command! Type /HELP for a list of commands\n'
            self.chat_window._insert('Server', new_msg)

    def _pause(self, toggle=None):
        '''
           Usage: /PAUSE <(on/off)> --> This will pause the channel's 'chatter'

           Pass in '/PAUSE on' to turn on pause or

           use '/PAUSE off' to turn off pause 'unpause'.
        '''
        if toggle is None or toggle not in ['on', 'off']:
            return self.command_error(self._pause.__doc__)
        if toggle == 'on':
            self.paused = True
        if toggle == 'off':
            self.paused = False

    def _reconnect(self, channel=None):
        '''
           Usage: /RECONNECT (optional <channel>) --> Set-up connection from\
                                                      inside the chat window.
        '''
        self.conn = False
        if channel is None:
            self.client.close()
            self.client = ChatSocket(self.host, self.port, self.chat_window)
            self.server_login
        if channel:
            self.channel = channel
            self.client.close()
            self.client = ChatSocket(self.host, self.port, self.chat_window)
            self.server_login

    def _usermsg(self, msg, nick=None):
        '''
           Usage: /MSG <nick> <msg> --> Message a user off channel.
        '''
        if nick is None:
            return self.command_error(self._usermsg.__doc__)
        else:
            new_msg = 'privmsg {} {} :\r\n'.format(nick, msg)
            self.client.sendall(new_msg)
            self.chat_window._insert(self.nick, '{}: {}\n'.format(nick, msg), 'user')
                            
    def _log(self, toggle=None):
        '''
           Usage: /LOG <(on/off)> --> Logs the chat in current channel to a file.

           Pass in '/LOG on' to open the log or

           use '/LOG off' to close the log. 
        '''
        if toggle is None or toggle not in ['on', 'off']:
            return self.command_error(self._log.__doc__)
        if toggle == 'on':
            self.logging = True
            self.log_file = open(os.path.join(os.environ['HOME'], 'chat_log.txt'), 'a')
            self.log_file.write(' -- {} --\n'.format(time.ctime()))
        if toggle == 'off':
            if self.logging:
                self.log_file.close()
            self.logging = False

    def command_error(self, cmd_doc):
        self.chat_window._insert('Server', '{}\n'.format(cmd_doc))

    def channel_msg(self, msg):
        msg_tokens = msg.split()
        channel = msg_tokens[0]
        if isinstance(self.channel, list) and channel not in self.channel:
            return self.command_error('Multiple channels open, specify a channel')
        elif isinstance(self.channel, list) and channel in self.channel:
            chan_msg = 'privmsg {} :\r\n'.format(msg)
            self.client.sendall(chan_msg)
        else:
            chan_msg = 'privmsg {} :{} \r\n'.format(self.channel, msg)
            self.client.sendall(chan_msg)
        self.chat_window._insert(self.nick, '', 'user');
        for token in msg_tokens:
            self.parse_msg(token)
        self.chat_window._insert(0, '\n');
        if self.logging:
            self.log_file.write('{}\n'.format(msg))

    @property
    def create_window(self):
        self.root.geometry('700x450+400+165')
        self.scrollbar = Scrollbar(self.root)
        self.scrollbar.grid(column=1, rowspan=2, sticky=E+S+N)
        self.chat_window = ChatWindow(self.root, self.scrollbar)
        self.scrollbar.config(command=self.chat_window.yview)
        self.scrn_loop = self.chat_window.after(100, self.msg_buffer_chk)
        self.entry = Entry(self.root, bg='black', fg='green2', 
                           font=('incolsolata', 10), insertbackground='green2')
        self.entry.bind('<Return>', self.input_handle)
        self.entry.grid(row=1, column=0, sticky=S+E+W)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.chat_window._insert(0, 'ATTEMPTING TO CONNECT TO {} #{}\n'.format(
                                  self.host, self.channel))
        self.entry.focus_set()

    @property            
    def connection_drop(self):
        self.client.close()
        self.conn = False
        self.client = ChatSocket(self.host, self.port, self.chat_window)
        self.server_login
        return self.command_error('Connection Dropped!')

    @property                    
    def server_login(self):
        if self.password:
            self.client.sendall('PASS {}\r\n'.format(self.password))
        self.client.sendall('NICK {}\r\n'.format(self.nick))
        userdata = 'USER {} {} servername :{}\r\n'.format(self.nick, self.host,
                                                                 self.user)
        self.client.sendall(userdata) 
        self.client.sendall('JOIN #{}\r\n'.format(self.channel.strip('#')))

    @property
    def server_pong(self):
        self.client.sendall('PONG {}\r\n'.format(self.recv_msg[1]))
        self.chat_window._insert('Server', 'Channel Ping@ ==> {}\n'.format(time.ctime()))

    def buffer_data_handle(self, buffer_data):
        if not buffer_data:
            self.connection_drop
            return
        for i in filter(None, buffer_data.split('\r\n')):
            self.recv_msg = list(map(self.ln_strip, i.split()))
            if self.recv_msg[0] == 'PING':
                self.server_pong
            elif len(self.recv_msg) >= 3: 
                self.msg_handle()       

    def channel_join(self, user, channel):
        if user == self.nick and not isinstance(self.channel, list):
            self.channel = channel 
            if not self.conn:
                self.chat_window._insert(0, 'SUCCESSFULLY CONNECTED TO {}\n'.format(
                                                                      self.host))
            self.chat_window._insert(0, 'SUCCESSFULLY JOINED {}\n'.format(channel))
        elif user != self.nick and self.verbose:
            if isinstance(self.channel, list) and channel not in self.channel:
                self.channel.append(channel)
            else:
                self.channel = channel
            new_msg = 'entered --> {}\n'.format(channel)
            self.chat_window._insert(user, new_msg, 'enter')

    def channel_quit(self, user, chan): 
        if user != self.nick and self.verbose:
            new_msg = 'left --> {}\n'.format(chan)
            self.chat_window._insert(user, new_msg, 'leave')

    def parse_msg(self, token):
        if token.startswith('http'):
            self.chat_window.tag_config(token, underline=1)
            self.chat_window.tag_bind(token, '<Enter>', 
                                   lambda e: self.chat_window.config(cursor='hand2'))
            self.chat_window.tag_bind(token, '<Leave>', 
                                   lambda e: self.chat_window.config(cursor=''))
            self.chat_window.tag_bind(token, '<Button-1>', 
                                   lambda e: self.open_link(e))
            self.chat_window._insert(0, token)
            self.chat_window._insert(0, ' ')
        else:
            try: # XXX catch unicode
                self.chat_window._insert(0, '{} '.format(token))
            except TclError:
                self.chat_window._insert(0, '~unicodeErr? ')

    def open_link(self, tk_event):
        link = self.chat_window.tag_names(CURRENT)[0]
        firefox_ps = subprocess.Popen(['firefox', link])
        firefox_ps.wait()

    def chat_msg(self, channel, user, msg):
        if msg[0] == self.nick and channel != self.nick:
            self.chat_window._insert(user, '', 'directed')
        elif channel == self.nick:
            self.chat_window._insert(user, '', 'private')
            #msg.insert(0, user + ': ') # XXX set pos arg
        else:
            self.chat_window._insert(user, '', 'response')
        for token in msg:
            self.parse_msg(token)
        self.chat_window._insert(0, '\n')
        if self.logging:
            self.log_file.write('{}\n'.format(' '.join(msg)))

    def server_reply_msg(self, user, cmd):
        self.server = user
        self.rspd.server = user
        if self.conn:
            try:
                reply = self.server_reply[cmd]
                reply(self.recv_msg[3:])
            except KeyError:
                pass 
        if cmd == '366':
            self.conn = True

    def input_handle(self, event):
        msg = self.entry.get()
        self.entry.delete(0, 'end')
        if not msg: return
        if msg.startswith('/'):
            msg = msg.split() + [None]
            msg_cmd = msg[0][1:].lower()
            command = self.commands.get(msg_cmd)
            if command and msg_cmd != 'msg' and msg_cmd != 'suser':
                command(msg[1])
            elif command and msg_cmd == 'msg':
                command(b' '.join(msg[2:-1]), msg[1])
            elif command and msg_cmd == 'suser':
                command(msg[1], msg[2])
            else:
                if self.scrollbar.get()[1] == 1.0:
                    self.chat_window.see(END)
                return self.command_error('Unknown Command! Type /HELP for\
                                           list of commands\n')
        else:
            self.channel_msg(msg) 

    def msg_buffer_chk(self):
        socket_data = select.select([self.client.fileno], [], [], 0.01)
        if socket_data[0]:
            client_msg = self.client.recvfrom(4096)
            self.buffer_data_handle(client_msg)
        self.root.update_idletasks()
        self.scrn_loop = self.chat_window.after(100, self.msg_buffer_chk)
    
    def msg_handle(self):
        user, cmd, channel = self.recv_msg[:3]  
        user = user.split('!')[0].strip(':')
        if user.endswith('.freenode.net'): 
            self.server_reply_msg(user, cmd)
        if cmd == 'PRIVMSG' and user not in self.blocked and not self.paused:
            self.chat_msg(channel, user, self.recv_msg[3:])
        if cmd == 'JOIN':
            self.channel_join(user, channel)
        if cmd == 'QUIT':
            self.channel_quit(user, channel)


class ChatWindow(Text):

    def __init__(self, master, scrollbar):
        super(Text, self).__init__(master, 'text')
        self.scrollbar = scrollbar
        self.fg_color = 'black'
        self.config(bg=self.fg_color, fg='green2')
        self.config(wrap=WORD)
        self.config(yscrollcommand=self.scrollbar.set)
        self.grid(row=0, column=0, stick=N+S+E+W)
        self.bg_color = {'server':'gold', 'user':'turquoise1', 
                         'response':'green2', 'enter':'red2',
                         'directed':'violetred1', 'private':'purple',
                         'leave':'royal blue'}

    def _insert(self, name, message, state=None):
        self.config(state=NORMAL)
        if isinstance(name, str):
            self.prefix(name, state)
        self.insert(END, message)
        if self.scrollbar.get()[1] == 1.0:
            self.see(END)
        self.config(state=DISABLED)

    def prefix(self, name, state=None):   
        startp = float(self.index(END)) - 1
        endp = float(self.index(END)) - 0.84
        prefix_name = '{:<16}| '.format(name)
        self.insert(END, prefix_name)
        if name == 'Server':
            prefix_name_tag = state = name.lower()
        elif state == 'user':
            prefix_name_tag = name
        else:
            prefix_name_tag = 'peer_{}'.format(state)
        self.tag_add(prefix_name_tag, startp, endp)
        self.tag_config(prefix_name_tag, background=self.bg_color[state],
                                         foreground=self.fg_color)

#!/usr/bin/env python
#-*- coding: utf-8 -*-

from Tkinter import *


class Response(object):

    def __init__(self, screen, nick, server=None):
        self.screen = screen
        self.nick = nick
        self.server = server

    @property
    def server_line(self):
        self.screen.insert(END, "Server          | ")
        pos = float(self.screen.index(END)) - 1
        self.screen.tag_add("server", str(pos), str(pos + 0.16))
        self.screen.tag_config("server", background="gold",
                                         foreground="black")

    def whois_user_repl(self, user_data):
        server_repl = 'User: %s' % (user_data[1] + '@' + user_data[2] + '\n')
        self.server_line 
        self.screen.insert(END, server_repl)
        self.screen.see(END)

    def whois_chan_repl(self, chan_data):
        if len(chan_data) == 2:
            self.server_line
            server_repl = ('Real Name: %s\n' % chan_data[0])
            self.screen.insert(END, server_repl)
            self.server_line
            self.server_repl = ('Server: %s\n' % chan_data[1].strip(':'))
            self.screen.insert(END, server_repl)
            self.screen.see(END)

    def names_repl(self, userlist):
        if any(i.endswith('.freenode.net') for i in userlist[2:]):
            pass
        else:
            server_repl = ('Users available on %s:\n' + '=' * 25 + '\n') % userlist[1]
            for usr in userlist[2:]:
                server_repl += ('  ~' + usr.strip(':@') + '\n')
            self.server_line 
            self.screen.insert(END, server_repl)
            self.screen.see(END)

    def info_repl(self, server_data):
            server_data = ' '.join(i.strip(':') for i in server_data)
            self.server_line 
            self.screen.insert(END, server_data + '\n')
            self.screen.see(END)

    def links_repl(self, server_data):
        link_info = ' '.join(i for i in server_data[3:])
        self.server_line 
        self.screen.insert(END, link_info + '\n')
        self.screen.see(END)

    def perm_denied_repl(self, server_response):
        server_response = ' '.join(server_response).strip(':')
        self.server_line 
        self.screen.insert(END, server_response + '\n')
        self.screen.see(END)

    def rate_lim_repl(self, server_response):
        server_response = ' '.join(server_response[1:]).strip(':')
        self.server_line 
        self.screen.insert(END, server_response + '\n')
        self.screen.see(END)

    def server_com_repl(self, server_coms):
        self.server_line 
        self.screen.insert(END, '%s\n' % server_coms[0])
        self.screen.see(END)

    def server_con_repl(self, server_connections):
        server_connections = ' '.join(server_connections)
        self.server_line 
        self.screen.insert(END, server_connections + '\n')
        self.screen.see(END)

    def server_utme_repl(self, server_data):
        server_data = ' '.join(server_data[:9]).strip(':')
        self.server_line 
        self.screen.insert(END, server_data + '\n')
        self.screen.see(END)

    def clnt_auth_repl(self, client_data):
        client_data = ' '.join(client_data)
        self.server_line 
        self.screen.insert(END, client_data + '\n')
        self.screen.see(END)

    def server_ver(self, server_data):
        self.server_line 
        self.screen.insert(END, 'Server Version: %s\n' % server_data[0])
        self.screen.see(END)

    def server_aux(self, server_data):
        self.server_line 
        self.screen.insert(END, ' '.join(server_data) + '\n')
        self.screen.see(END)

    def chan_topic(self, topic):
        self.server_line 
        self.screen.insert(END, 'Topic for %s\n' % (' '.join(topic)))
        self.screen.see(END)

    def nick_inuse(self, msg):
        self.server_line 
        self.screen.insert(END, ' '.join(msg[:6]) + '\n')
        self.screen.insert(END, 'Use the /NICK <nick> command to choose a new nick\n')
        self.screen.see(END)

    def list_repl(self, list_data):
        topic = ' '.join(list_data)
        self.server_line 
        self.screen.insert(END, "--" + topic.split(' :')[0] + "--\n")
        try:
            self.screen.insert(END, topic.split(' :')[1] + '\n')
        except IndexError:
            pass
        self.screen.see(END)

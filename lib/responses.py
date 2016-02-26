#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
from collections import defaultdict

from lib import END


class Response(object):

    def __init__(self, chat_window, nick):
        self.chat_window = chat_window
        self.nick = nick
        self.ln_strip = lambda s: s.strip(':')
        self.chan = None
        self.chan_names = defaultdict(list)
        self.comp_chan_names = False
        self.log_links = False
        self.server_cmds = list()

    def whois_user_repl(self, user_data):
        server_repl = 'User: {}@{}\n'.format(user_data[1], user_data[2])
        self.chat_window._insert('Server', server_repl)

    def whois_chan_repl(self, chan_data):
        if len(chan_data) != 2: return
        server_repl = 'Real Name: {}\n'.format(chan_data[0])
        self.chat_window._insert('Server', server_repl)
        self.server_repl = 'Server: {}\n'.format(chan_data[1].strip(':'))
        self.chat_window._insert('Server', server_repl)

    def names_repl(self, userlist):
        self.chan = userlist[1] # XXX python3 index error out of range
        self.chan_names[userlist[1]] += map(self.ln_strip, userlist[2:])

    def end_names_repl(self, server_end):
        if self.comp_chan_names and len(self.chan_names) < 2: return
        if not self.comp_chan_names:
            if not self.chan:
                self.chat_window._insert('Server', 'Channel does not exist\n')
            else:
                self.chat_window._insert('Server', 'Total Users in {}: {}\n'.format( 
                                   (self.chan, len(self.chan_names[self.chan]))))
                self.chat_window._insert('Server', '{}\n'.format(' '.join(self.chan_names[self.chan])))
        else:
            self.comp_chan_names = False
            users = [j for i in self.chan_names.values() for j in i]
            like_users = {i for i in users if users.count(i) > 1}
            self.chat_window._insert('Server', 'Shared users {}\n'.format(len(like_users)))
            self.chat_window._insert('Server', '{}\n'.format(' '.join(like_users)))
        self.chan = None
        self.chan_names = defaultdict(list)

    def info_repl(self, server_data):
        server_info_repl = ' '.join(map(self.ln_strip, server_data))
        self.chat_window._insert('Server', '{}\n'.format(server_info_repl))

    def links_repl(self, server_data):
        link_info = ' '.join(server_data[3:])
        self.chat_window._insert('Server', '{}\n'.format(link_info))

    def perm_denied_repl(self, server_response):
        server_response = ' '.join(server_response).strip(':')
        self.chat_window._insert('Server', '{}\n'.format(server_responses))

    def rate_lim_repl(self, server_response):
        server_response = ' '.join(server_response[1:]).strip(':')
        self.chat_window._insert('Server', '{}\n'.format(server_responses))

    def server_com_repl(self, server_coms):
        self.server_cmds.append(server_coms[0])

    def server_com_end(self, server_end):
        self.chat_window._insert('Server', 'Total Server Commands: {}\n'.format( 
                                        len(self.server_cmds)))
        self.chat_window._insert('Server', '{}\n'.format(self.server_cmds))
        self.server_cmds = list()

    def server_con_repl(self, server_connections):
        server_connections = ' '.join(server_connections)
        self.chat_window._insert('Server', '{}\n'.format(server_connections))

    def server_utme_repl(self, server_data):
        server_data = ' '.join(server_data[:9]).strip(':')
        self.chat_window._insert('Server', '{}\n'.format(server_data))

    def clnt_auth_repl(self, client_data):
        client_data = ' '.join(client_data)
        self.chat_window._insert('Server', '{}\n'.format(client_data))

    def server_ver(self, server_data):
        self.chat_window._insert('Server', 'Server Version: {}\n'.format(server_data[0]))

    def server_aux(self, server_data):
        self.chat_window._insert('Server', '{}\n'.format(' '.join(server_data)))

    def chan_topic(self, topic):
        self.chat_window._insert('Server', 'Topic for {}\n'.format(' '.join(topic)))

    def nick_inuse(self, msg):
        self.chat_window._insert('Server', '{}\n'.format(' '.join(msg[:6])))
        self.chat_window._insert('Server', 'Use the /NICK <nick> command to choose a new nick\n')

    def list_repl(self, list_data):
        topic = ' '.join(list_data)
        self.chat_window._insert('Server', '-- {} --\n'.format(topic.split(' :')[0]))
        try:
            self.chat_window._insert('Server', '{}\n'.format(topic.split(' :')[1]))
        except IndexError:
            pass
        if self.log_links:
            with open(os.getcwd() + '/.link.txt', 'a') as f:
                f.write(('=' * 25) + '\n')
                f.write('-- {} --\n'.format(topic.split(' :')[0]))
                try:
                    f.write('{}'.format(topic.split(' :')[0]))
                except IndexError:
                    pass
                f.write('\n')


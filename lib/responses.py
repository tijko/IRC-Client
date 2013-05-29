#!/usr/bin/env python
#-*- coding: utf-8 -*-

class Response(object):

    def __init__(self, nick, server=None):
        self.nick = nick
        self.server = server

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

    def list_repl(self, list_data):
        topic = ' '.join(list_data)
        print "--" + topic.split(' :')[0] + "--"
        print topic.split(' :')[1] + '\n'

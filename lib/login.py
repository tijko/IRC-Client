#!/usr/bin/env python
# -*- coding: utf-8 -*-

from client import Client
import ConfigParser
import os

from lib import Entry, Label, Button, Checkbutton, IntVar, END


class Login(object):

    def __init__(self, root, runclient_cb):
        self.root = root
        self.runclient_cb = runclient_cb
        self.chk = IntVar()
        self.host_label = Label(self.root, text="Host:").grid(row=0, 
                                                              column=0, 
                                                              padx=5, 
                                                              sticky="W")
        self.host = Entry(self.root, relief="ridge")
        self.host.grid(row=0, column=1, pady=(15,5))
        self.port_label = Label(self.root, text="Port:").grid(row=1, 
                                                              column=0, 
                                                              padx=5, 
                                                              sticky="W")
        self.port = Entry(self.root)
        self.port.grid(row=1, column=1, pady=5)
        self.channel_label = Label(self.root, text="Channel:").grid(row=2, 
                                                                    padx=5, 
                                                                    sticky="W")
        self.channel = Entry(self.root)
        self.channel.grid(row=2, column=1, pady=5)
        self.user_label = Label(self.root, text="User:").grid(row=3, 
                                                              padx=5, 
                                                              sticky="W")
        self.user = Entry(self.root)
        self.user.grid(row=3, column=1, pady=5)
        self.nick_label = Label(self.root, text="Nick:").grid(row=4, 
                                                              padx=5, 
                                                              sticky="W")
        self.nick = Entry(self.root)
        self.nick.grid(row=4, column=1, pady=5)
        self.password_label = Label(self.root, text="Password:").grid(row=5, 
                                                                      padx=5, 
                                                                      sticky="W")
        self.password = Entry(self.root, show='*')
        self.password.grid(row=5, column=1, pady=5)
        self.login_fields = [self.port, self.host, self.channel, 
                             self.user, self.nick, self.password]
        self.ok = Button(self.root, text="ok", command=self.runclient_cb)
        self.ok.grid(row=6, column=0, padx=10, pady=10)
        self.cancel = Button(self.root, text="cancel", command=self.cancel_session)
        self.cancel.grid(row=6, column=1, padx=10, pady=10)
        self.chkbx = Checkbutton(self.root, text="remember me", variable=self.chk)
        self.chkbx.grid(row=7, column=0, padx=5, pady=5)
        self.load_saved()

    def load_saved(self):
        if os.path.isfile(os.environ['HOME'] + '/.pychat'):
            login_settings = ConfigParser.ConfigParser()
            login_settings.read(os.environ['HOME'] + '/.pychat')
            credentials = login_settings.items('PyChat_Login')
            for field, value in credentials:
                getattr(self, field).insert(0, value)
            self.chkbx.select()

    def save_login(self, credentials):
        home_dir = os.environ['HOME']
        login_file = ConfigParser.RawConfigParser()
        login_file.add_section('PyChat_Login')
        for credential in credentials:
            login_file.set('PyChat_Login', credential, credentials[credential])
        with open(home_dir + '/.pychat', 'wb') as f:
            login_file.write(f)        

    def login_credentials(self):
        fields = ['port', 'host', 'channel', 'user', 'nick', 'password']
        credentials = map(getattr(Entry, 'get'), self.login_fields)
        user_login_credentials = dict(zip(fields, credentials))
        try:
            user_login_credentials['port'] = int(user_login_credentials['port'])
        except ValueError:
            self.port.delete(0, END)
            self.port.insert(0, 'port must be an integer')
            return
        if self.chk.get():
            self.save_login(user_login_credentials)
        return user_login_credentials

    def cancel_session(self):
        self.root.destroy()


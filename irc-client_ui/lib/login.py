#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
from client import Client

import os


class Login(object):

    def __init__(self):
        self.root = Tk()
        self.root.geometry("300x275+400+100")
        self.chk = IntVar()
        self.PATH = os.path.join(os.environ['HOME'], '.irc-client/')
        if not os.path.isdir(self.PATH):
            os.mkdir(self.PATH)
        self.create_window()
            
    def create_window(self):
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
        self.ok = Button(self.root, text="ok", command=self.login_credentials)
        self.ok.grid(row=6, column=0, padx=10, pady=10)
        self.cancel = Button(self.root, text="cancel", command=self.cancel_session)
        self.cancel.grid(row=6, column=1, padx=10, pady=10)
        self.chkbx = Checkbutton(self.root, text="remember me", variable=self.chk)
        self.chkbx.grid(row=7, column=0, padx=5, pady=5)
        self.load_saved()
        self.root.mainloop()

    def load_saved(self):
        if os.path.isfile(self.PATH + 'login_data'):
            with open(self.PATH + 'login_data') as f:
                login_data = f.read().split()
            self.host.insert(0, login_data[0]) 
            self.port.insert(0, int(login_data[1]))
            self.channel.insert(0, login_data[2])
            self.user.insert(0, login_data[3])
            self.nick.insert(0, login_data[4])
            self.password.insert(0, login_data[5])
            self.chkbx.select()

    def login_credentials(self):
        try:
            port = int(self.port.get())
            self.port.delete(0, END)

            host = self.host.get()
            self.host.delete(0, END)

            channel = self.channel.get()
            self.channel.delete(0, END)
    
            user = self.user.get()
            self.user.delete(0, END)

            nick = self.nick.get()
            self.nick.delete(0, END)

            password = self.password.get()
            self.password.delete(0, END)

            self.root.destroy()
            if self.chk.get():
                with open(self.PATH + 'login_data', 'w') as f:
                    for i in [host, str(port), channel, user, nick, password]:
                        f.write(i + '\n')
            else:
                try:
                    os.remove(self.PATH + 'login_data')
                except OSError:
                    pass
            client = Client(host=host, 
                            port=port, 
                            channel=channel, 
                            user=user, 
                            nick=nick, 
                            password=password)
            client.root.mainloop()
        except ValueError:
            self.port.delete(0, END)
            self.port.insert(0, "Port must be an interger!")

    def cancel_session(self):
        self.root.destroy()


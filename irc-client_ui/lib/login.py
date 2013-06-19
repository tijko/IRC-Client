#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
from client import Client


class Login(object):

    def __init__(self):
        self.root = Tk()
        self.root.geometry("250x235+400+100")

        self.host_label = Label(self.root, text="Host:").grid(row=0, 
                                                              column=0, 
                                                              padx=5, 
                                                              sticky="W")
        self.host = Entry(self.root)
        self.host.grid(row=0, column=1, pady=5)

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
        self.password = Entry(self.root)
        self.password.grid(row=5, column=1, pady=5)

        self.ok = Button(self.root, text="ok", command=self.login_credentials)
        self.ok.grid(row=6, column=0, padx=10, pady=10)

        self.cancel = Button(self.root, text="cancel", command=self.cancel_session)
        self.cancel.grid(row=6, column=1, padx=10, pady=10)
        
        self.root.mainloop()

    def login_credentials(self):
        host = self.host.get()
        self.host.delete(0, END)

        port = int(self.port.get())
        self.port.delete(0, END)

        channel = self.channel.get()
        self.channel.delete(0, END)

        user = self.user.get()
        self.user.delete(0, END)

        nick = self.nick.get()
        self.nick.delete(0, END)

        password = self.password.get()
        self.password.delete(0, END)

        self.root.destroy()
        client = Client(host=host, 
                        port=port, 
                        channel=channel, 
                        user=user, 
                        nick=nick, 
                        password=password)
        client.root.mainloop()

    def cancel_session(self):
        self.root.destroy()


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import Tk 
from lib.login import Login
from lib.client import Client


class PyChat(object):

    def __init__(self):
        self.root = Tk()
        self.root.geometry("300x275+400+100")

    def login(self):
        self.login = Login(self.root, self.create_client)

    def run(self):
        self.root.mainloop()

    def create_client(self):
        credentials = self.login.login_credentials()
        credentials['root'] = self.root
        credentials['port'] = int(credentials['port'])
        self.reset()
        self.client = Client(**credentials)

    def reset(self):
        for element in self.root.winfo_children():
            element.destroy()
                    

if __name__ == '__main__':
    pychat = PyChat()
    pychat.login()
    pychat.run()

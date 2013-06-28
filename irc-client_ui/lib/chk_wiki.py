#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import Queue
from threading import Thread
from BeautifulSoup import BeautifulSoup
from Tkinter import *


class Wiki(Thread):

    def __init__(self, client, window, prefix, query, wiki_q):
        super(Wiki, self).__init__()
        self.client = client
        self.window = window
        self.prefix_line = prefix
        self.query = query
        self.wiki_q = wiki_q

    def run(self):
        self.wiki_lookup()

    def wiki_lookup(self):
        page = 0
        wiki = 'http://en.wikipedia.org/w/index.php?action=render&title='
        req = requests.get(wiki + self.query)
        soup = BeautifulSoup(req.content)
        p_tags = soup.findAll('p')
        if any(i.text=='It may also refer to:' for i in p_tags) or len(p_tags) <= 3:
            a_tags = soup.findAll("a")
            for tag in a_tags:
                self.prefix_line("Server")
                tag_line = "[%d] -- %s\n" % (a_tags.index(tag) + 1, tag['href'])
                self.window.insert(END, tag_line)
                self.window.see(END)
            self.window.insert(END, "Do you want to do a look-up on any of these?\n")
            self.window.insert(END, "Enter '/WHATIS #from_above' or '/WHATIS n'\n")
            self.window.see(END)
            limit = time.time()
            while not self.wiki_q.queue:
                current = time.time()
                try:
                    search_index = self.wiki_q.get_nowait()
                    break
                except Queue.Empty:
                    pass
                if (current - limit) > 300:
                    self.client.search = False
                    return
            if search_index == 'n':
                self.client.search = False
                return
            else:
                self.query = a_tags[int(search_index) - 1]['href'].split('/')[-1]
                self.wiki_lookup()
        else:
            while True:
                self.prefix_line("Server")
                self.window.insert(END, p_tags[page].text + '\n')
                self.window.see(END)
                if page == len(p_tags) - 1:
                    self.prefix_line("Server")
                    self.window.insert(END, "End of File\n")
                    self.window.see(END)
                    self.client.search = False
                    return
                self.prefix_line("Server")
                self.window.insert(END, "More? (y or n)\n")
                self.window.see(END)
                limit = time.time()
                while not self.wiki_q.queue:
                    current = time.time()
                    try:
                        expand = self.wiki_q.get_nowait()
                        break
                    except Queue.Empty:
                        pass
                    if (current - limit) > 300:
                        self.client.search = False
                        return
                if expand == 'y':
                    page += 1
                else:
                    self.client.search = False
                    return

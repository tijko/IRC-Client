#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import Queue
from threading import Thread
from BeautifulSoup import BeautifulSoup

from lib import END


class Wiki(Thread):

    def __init__(self, client, window, prefix, query, wiki_q):
        super(Wiki, self).__init__()
        self.wiki_url = 'http://en.wikipedia.org/w/index.php?action=render&title='
        self.client = client
        self.window = window
        self.prefix_line = prefix
        self.query = query
        self.wiki_q = wiki_q

    def display_alternate_articles(self, content):
        a_tags = content.findAll("a")
        for tag in a_tags:
            self.prefix_line("Server")
            tag_line = "[%d] -- %s\n" % (a_tags.index(tag) + 1, tag['href'])
            self.window.insert(END, tag_line)
            self.window.see(END)
        self.prefix_line("Server")
        self.window.insert(END, "Do you want to do a look-up on any of these?\n")
        self.prefix_line("Server")
        self.window.insert(END, "Enter '/WHATIS #from_above' or '/WHATIS n'\n")
        self.window.see(END)
        return self.select_alternate_article(a_tags)

    def select_alternate_article(self, links):
        choice = self.make_selection()
        if choice == 'n' or not choice.isdigit(): 
            return 
        query = links[int(choice) - 1]['href'].split('/')[-1]
        return self.make_request(query)

    def make_selection(self):
        start_timeout = time.time()
        selection = None
        while selection is None:
            try:
                selection = self.wiki_q.get_nowait()
            except Queue.Empty:
                current = time.time()
                if (current - start_timeout > 300):
                    selection = 'n'
        return selection

    def make_request(self, query):
        req = requests.get(self.wiki_url + query)
        soup = BeautifulSoup(req.content)
        p_tags = soup.findAll('p')
        if any(i.text=='It may also refer to:' for i in p_tags) or len(p_tags) <= 3:
            return self.display_alternate_articles(soup)
        else:
            return p_tags

    def display_eof(self):
        self.prefix_line("Server")
        self.window.insert(END, "End of File\n")
        self.window.see(END)
        self.client.search = False

    def run(self):
        page = 0
        page_content = self.make_request(self.query)
        if page_content is None:
            self.client.search = False
        while self.client.search:
            self.prefix_line("Server")
            self.window.insert(END, page_content[page].text + '\n')
            self.window.see(END)
            if page == len(page_content) - 1:
                self.display_eof()
                self.client.search = False
            else:
                self.prefix_line("Server")
                self.window.insert(END, "More? (y or n)\n")
                self.window.see(END)
                expand = self.make_selection()
                if expand == 'y':
                    page += 1
                else:
                    self.client.search = False

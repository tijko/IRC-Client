# --*-- coding: UTF-8 --*--
#!/usr/bin/env python

import requests
from BeautifulSoup import BeautifulSoup


def wiki_lookup(query):
    page = 0
    wiki = 'http://en.wikipedia.org/w/index.php?action=render&title='
    req = requests.get(wiki + query)
    soup = BeautifulSoup(req.content)
    p_tags = soup.findAll('p')
    if len(p_tags) <= 2:
        a_tags = soup.findAll("a")
        for tag in a_tags:
            print "[%d] -- %s" % (a_tags.index(tag) + 1, tag['href'])
        choice = raw_input("Do you want to do a look-up on any of these?(y or n): ")
        if choice.lower() == 'y':
            lookup = raw_input("Select the number: ")
            query = a_tags[int(lookup) - 1]['href'].split('/')[-1]
            wiki_lookup(query)
    else:
        while True:
            print p_tags[page].text
            if page == len(p_tags) - 1:
                print "End of File"
                return
            more = raw_input("More? (y or n)=> ")
            if more.lower() == 'y':
                page += 1
            else:
                break
    return


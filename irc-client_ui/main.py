#!/usr/bin/env python

from lib.client import Client


def main():
    user = ""
    nick = ""
    host = ""
    password = "" 
    port = 0
    channel = ""
    c = Client(user=user, 
               nick=nick, 
               host=host, 
               port=port, 
               channel=channel, 
               password=password)
    c.mainloop()
                    

if __name__ == '__main__':
    main()

#!/usr/bin/env python

from lib.client import Client


def main():
    print '=' * 40
    user = raw_input('Username: ')
    nick = raw_input('Nickname: ')
    host = raw_input('Host: ')
    while True:
        reg_option = raw_input('Do you wish to register? (y or n): ')
        if reg_option.lower() == 'n':
            password = None
            break
        if reg_option.lower() == 'y':
            password = raw_input('Enter your password: ')
            break
    while True:
        try:
            port = int(raw_input('Port: '))
            break
        except ValueError:
            print 'Port must be an integer!'
            pass
    channel = raw_input('Channel: ')
    Client(user=user, 
           nick=nick, 
           host=host, 
           port=port, 
           channel=channel, 
           password=password)


if __name__ == '__main__':
    main()

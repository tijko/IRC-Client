#!/usr/bin/env python

from lib.client import Client


def main():
    user = raw_input('Username: ')
    nick = raw_input('Nickname: ')
    host = raw_input('Host: ')
    while True:
        try:
            port = int(raw_input('Port: '))
            break
        except ValueError:
            pass
    channel = raw_input('Channel: ')
    Client(user=user, nick=nick, host=host, port=port, channel=channel)


if __name__ == '__main__':
    main()

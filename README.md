IRC-Client
==========

A thin client for irc chat. This client has a very barebones interface
using Tkinter but, has some text highlighting applied for different messages.

IRC-Client only allows chatting on one channel at a time, so no other channel-tabs right now.

There is hyperlink recognition, they're underlined. If you left click on any 
links that are automatically __underlined__ and you have firefox browser
installed they will open in a new __firefox__ window.
#### usage:

When inputting any command use a backslash then the command you wish to call,
entering `/help` will show all other available commands:

    Commands <<<help - links - topic - unblock - names - reconnect - quit - pause - 
                stats - whois - nick - version - whereami - noise - msg - part - whatis -
                log - info - join - blocklist - list - whowas - whoami - block>>>

You can also use `/help <command>` for any valid command, if you want to see how to use it or
what the command does.

#### note:

This client does use two libraries that are not included in python's standard lib.
They are `BeautifulSoup` and `Requests`, so those will need to be pip-installed, 
downloaded from their site, or installed using whichever package manager your system
uses.

IRC-Client
==========

A thin client for irc chat on freenode.net.  You can log onto your favorite irc-channel from you commandline 
to send a quick message or two.  Or for common use if you prefer the terminal to another interface.

You can send and receive standard messages aswell as a handful of other irc-commands.

IRC-Client only allows chatting on one channel at a time, so when joining another channel you will automatically 
part from the current channel, if any.

#### usage


    python main.py
    Username: tijko-client
    Nickname: tijko 
    Host: irc.freenode.net
    Port: 6667
    Channel: favorite-channel

    SUCCESSFULLY CONNECTED TO irc.freenode.net
    SUCCESSFULLY JOINED #favorite-channel

    /help
    commands:
    < INFO  QUIT  PART  STATS  NAMES  LINKS  JOIN  HELP  WHOIS  >


This small sample shows how you would log on to "favorite-channel" then use the `/help` command to show the rest of 
the clients command options. 

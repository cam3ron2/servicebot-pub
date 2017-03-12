ServiceNow monitoring tool that uses the Slack API. <br/><br/>
The purpose of this script is to provide support teams working out of ServiceNow
with the ability to collaborate and divide work using slack. I find that in
Slack it is easier to keep track of what teammates are doing and communicate,
especially since we have it open all day anyways. I hope this helps someone
else as well. This script will monitor a set of queues for new tickets and then
broadcast them to a slack channel with clickable links.

Requirements:
Python <= 3.6
  sqlite3
  slackclient
  selenium
    PhantomJS http://phantomjs.org/

Using this script:
Currently, I run this script as a cron with a 1m interval. As I have more free
time to work on this project, that will not be necessary.

My cron that I use is
* * * * * unset QT_QPA_PLATFORM && cd {path to script} && ./watchdog.py
(the `unset QT_QPA_PLATFORM` bit is necessary on my arch system due to some
bullshit with QT5. You may or may not need to do the same thing)


You are welcome to use this script as you see fit under the terms of the GPL.
Accepting feature and pull requests, just make sure that the feature is not
already listed in the TODO section.

As a final note, this is being developed in my spare time, and changes will be
made as I am able to make them. Anyone using the script is encouraged to Submit
pull requests, and any help is greatly appreciated.

TODO:
The servicebot portion of this project allows team leaders to query the bot for
information about all open incidents. This is still very much a work in progress.
When team members respond to an incident that has been broadcast with "ack", the
bot will then mark the ticket in the database as being owned by them.
Team members can also add notes to incidents so that others can see what is going
on without the need to open ServiceNow and hunt for information.
When asked, the bot can also list all open incidents assigned to a team, and will
also list who is working on it and list any notes.

In the future, I also intend to add functionality that will assign the ticket to
whatever user "acks" the ticket. This will help reduce response time SLA's, and
will help to prevent SLA breaches.

The bot will also eventually monitor for "stale" tickets, IE tickets that have
been sitting in a queue for an extended period of time with no action taken.

Finally, in the future I intent to add SLA monitoring to the bot, so that it
will alert as tickets progress through their SLA or OLA to prevent breaches and
allow teams to more effectively respond to and prioritize incidents.

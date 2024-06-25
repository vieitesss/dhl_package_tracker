# DHL_package_tracker

I've made this script because I'm waiting for a [Voyager](https://www.zsa.io/voyager) keyboard, and I'm so exited that I can't stop reloading the web to see if there are any updates.

This Python script saves the last update message from DHL web and checks, every time it is executed, if the previous saved message is equal to the new message. If the messages are different, it uses [dunst](https://github.com/dunst-project/dunst) to send a notification to your computer, so you can see the change live.

# Prerequisites

- Only tested in Debian 12 (may or may not work in other distributions)
- python3
- dunst

# How to use

First of all is installing the requirements.

```bash
pip install -r requirements.txt
```

How I'm currently using it is through a cron job that runs it every minute. To setup a cron job you just have to do the following:

```bash
crontab -e
```

Include the following line at the end of the file.

```bash
*/1 * * * * XDG_RUNTIME_DIR=/run/user/$(id -u) /path/to/python3 /path/to/main.py <id> 
# For example
# */1 * * * * XDG_RUNTIME_DIR=/run/user/$(id -u) /usr/local/bin/python3 /home/user/main.py 123123123
```

- The "XDG..." thing is required, at least for me, to allow cron to send notifications.
- The number at the end must be your DHL package id.

# More

You can do with this script whatever you want. Tweak it to your liking.


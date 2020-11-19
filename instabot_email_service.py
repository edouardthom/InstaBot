#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BOT_GMAIL_ADDRESS = 'instabot.insights@gmail.com'
BOT_GMAIL_PASSWORD = ''

msg = MIMEMultipart('alternative')
msg['From'] = BOT_GMAIL_ADDRESS
msg['To'] = "edouard.thom@gmail.com"
msg['Subject'] = "This is TEST"



# Create the body of the message (a plain-text and an HTML version).
text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org"


# Record the MIME types of both parts - text/plain and text/html.
#part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

s = smtplib.SMTP(host='smtp.gmail.com', port=587)
s.starttls()
s.login(BOT_GMAIL_ADDRESS, BOT_GMAIL_PASSWORD)
       
# send the message via the server set up earlier.
s.send_message(msg)
s.quit()
        


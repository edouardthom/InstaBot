#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from instabot_run_variables import BOT_GMAIL_ADDRESS,BOT_GMAIL_PASSWORD
from instabot_data_api import dataAPI


def send_basic_insights_email(hours_back,email_destination,user):
    dataAPI().log(user,"send_basic_insights_email","INFO","start")
    todatetime = lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f")  
    limit_back = datetime.datetime.now()-datetime.timedelta(hours=hours_back)
    
    followers= dataAPI().get("followers",user)
    
    ### New followers
    new_follow_events = followers[followers.follow_time.apply(todatetime) >= limit_back]
    new_followers = list(new_follow_events.account_username.drop_duplicates())
    nb_new_followers = len(new_followers)
    
    if len(new_follow_events)==len(followers):
        nb_new_followers = "?"
        new_followers = []
    
    ### New unfollowers
    unfollowers = followers.dropna()
    new_unfollow_events = unfollowers[unfollowers.unfollow_time.apply(todatetime) >= limit_back]
    new_unfollowers = list(new_unfollow_events.account_username.drop_duplicates())
    nb_new_unfollowers = len(new_unfollowers)
    
    dataAPI().log(user,"send_basic_insights_email","INFO","data obtained")
    
    text = 'Hola {} !\n\n \
    I hope you are staying positive and testing negative. \n\n \
    Here are your account stats for the past {} hours : \n\n \
        - Number of new followers : {} \n \
        - Number of accounts that unfollowed you : {} \n\n \
        - Welcome some of your new followers : {} \n \
        - Some of the accounts that unfollowed you : {} \n\n \
    Good bye :) \n \
    Instagrobot'.format(user,hours_back,nb_new_followers,nb_new_unfollowers,
                            ", ".join(new_followers[:5]),
                            ", ".join(new_unfollowers[:5]))
    
    msg = MIMEMultipart()
    msg['From'] = BOT_GMAIL_ADDRESS
    msg['To'] = email_destination
    msg['Subject'] = "Account Insights"
    
    
    msg.attach(MIMEText(text, 'plain'))
    
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(BOT_GMAIL_ADDRESS, BOT_GMAIL_PASSWORD)
           
    s.send_message(msg)
    s.quit()
    dataAPI().log(user,"send_basic_insights_email","INFO","email successfully sent to the user")












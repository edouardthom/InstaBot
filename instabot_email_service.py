#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from instabot_run_variables import BOT_GMAIL_ADDRESS,BOT_GMAIL_PASSWORD
from instabot_data_api import dataAPI

def send_email(subject,text,email_destination,user):
    try:
        msg = MIMEMultipart()
        msg['From'] = BOT_GMAIL_ADDRESS
        msg['To'] = email_destination
        msg['Subject'] = subject
        
        msg.attach(MIMEText(text, 'plain'))
        
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls()
        s.login(BOT_GMAIL_ADDRESS, BOT_GMAIL_PASSWORD)
               
        s.send_message(msg)
        s.quit()
        dataAPI().log(user,"send_email","INFO","email successfully sent to {}".format(email_destination))
    except:
        dataAPI().log(user,"send_email","ERROR","failed to send email to {}".format(email_destination))

    
    

######################################## INSIGHTS EMAILS ########################################
# such emails are sent to the customers of the bot. It provides them diverse insights regarding #
# evolution of their audience                                                                   #
#################################################################################################

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
    
    subject = "Account Insights"
    send_email(subject,text,email_destination,user)
    dataAPI().log(user,"send_basic_insights_email","INFO","basic insights email successfully sent for user {}".format(user))


##################################### MAINTENANCE EMAILS ########################################
# such emails are sent to the developer maintaining the bot. They contain error reports         #
#################################################################################################

def send_bug_report_email(hours_back,email_destination,user):

    logs = dataAPI().get("logs",user)
    todatetime = lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S")  
    limit_back = datetime.datetime.now()-datetime.timedelta(hours=hours_back)
    
    logs = logs[logs.timestamp.apply(todatetime) >= limit_back]
    errors = logs[logs.seriousness=="ERROR"]
    nb_errors = len(errors)
    
    nb_errors_per_function = errors.groupby("function").message.agg(["count"]).reset_index()
    nb_errors_per_function = nb_errors_per_function.sort_values("count",ascending=False).reset_index(drop=True)
    
    errors = errors.drop("user",1)
    errors = errors.drop("seriousness",1).reset_index(drop=True)
    errors = errors.T.to_dict()
    
    text = 'Hola !\n\n \
    I hope you are staying positive and testing negative. \n\n \
    Here is the bug report for the past {} hours : \n\n \
        - Number of errors : {} \n\n \
        - Distribution of the errors across the functions : \n{} \n\n \
        - Details of the logs, ordered by timestamp :\n {} \n\n \
    Good bye :) \n \
    InstaBot🤖'.format(hours_back,nb_errors,
                       nb_errors_per_function,
                       json.dumps(errors, indent=4, sort_keys=True))
    text = text[:10000]
    
    subject = "Bug Report"
    send_email(subject,text,email_destination,user)
    dataAPI().log(user,"send_basic_insights_email","INFO","bug report email successfully sent for user {}".format(user))
    








   
    
    
    






#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings 
from math import ceil
from sys import argv
import datetime
import numpy as np
warnings.filterwarnings("ignore") #f**k warnings
from utilities import load_config_user
from instabot_functions import log_in,update_followers_data,unfollow_accounts,update_follow_actions_data,follow_accounts_from_hashtag,smart_sleep
from instabot_email_service import send_basic_insights_email,send_bug_report_email
from instabot_data_api import dataAPI
import instabot_data_api
instabot_data_api.STORE_LOGS = True 


user = argv[1]


############################################# Configuration bit for the user ###########################
config_file_name = "config.json"
variables = ["user_email","user_password","hashtags","max_follows_per_day",
             "hours_between_insights_emails","insights_email_hours_back",
             "send_bugreport_emails","dev_email","hours_between_bugreport_emails","bugreport_email_hours_back"]
config = load_config_user(user,variables,"config.json")
user_email = config["user_email"]
user_password = config["user_password"]
hashtags = config["hashtags"]
max_follows_per_day = config["max_follows_per_day"]
hours_between_insights_emails = config["hours_between_insights_emails"]
insights_email_hours_back = config["insights_email_hours_back"]
send_bugreport_emails = config["send_bugreport_emails"]
dev_email = config["dev_email"]
hours_between_bugreport_emails = config["hours_between_bugreport_emails"]
bugreport_email_hours_back = config["bugreport_email_hours_back"]
##########################################################################################################




### That loop runs once every [time_between_loops] seconds
# At each iteration we :
# step 1. log in
# step 2. update the followers data
# step 3. unfollow some accounts (to aoid following too many people)
# step 4. update the following data
# step 5. follow some people
# step 6. send an email containing insights
# step 7. send a bug report
# then we wait a bit until the next iteration 

# The following variables are set to reach the max number of follows per day, set in the settings 
# The main loop is designed so that there is ~1 loop per hour, and the bot sleeps 8 hours per day
nb_follows_per_hashtag = 2
nb_follows_per_loop = ceil(max_follows_per_day/16.0)
nb_hashtags_per_loop = ceil(nb_follows_per_loop/2.0)

loop_number = 0
dataAPI().log(user,"MAIN","INFO","Bot started for user {} !".format(user))
while 1:
    
    ## We run only during the 8 hours of awake time : approx. 8am to 12pm 
    now = datetime.datetime.now()
    if now.hour >= 0 and now.hour < 8:
        seconds_to_sleep = (8 - now.hour)*3600 - (now.minute)*60
        dataAPI().log(user,"MAIN","INFO","It's night time, time for the bot to sleep : approximately {} seconds".format(seconds_to_sleep))
        smart_sleep(seconds_to_sleep)
    
    
    dataAPI().log(user,"MAIN","INFO","loop {} start".format(loop_number))
    
    ### Step 1.
    driver = log_in(user_email,user_password,user,for_aws=False,headless=True)
    
    ### If login failure, we cannot pursue the loop, we retry
    if driver==0:
        dataAPI().log(user,"MAIN","INFO","failed to log-in and get the driver - restarting in 2 minutes...")
        smart_sleep(120)
        continue
    
    ### Step 2.
    success1 = update_followers_data(user,driver)
    
    ### Step 3.
    success2 = unfollow_accounts(user,driver)
    
    ### Step 4.
    success3 = update_follow_actions_data(user,driver)
    
    ### Step 5.
    success4 = []
    for _ in range(nb_hashtags_per_loop):
        hashtag = hashtags[np.random.randint(0,len(hashtags))]
        success = follow_accounts_from_hashtag(hashtag,user=user,
                                               nb_follows=nb_follows_per_hashtag,
                                               driver=driver)
        success4.append(success)
        smart_sleep(40)
    driver.close()
    
    ### Step 6.
    if loop_number%hours_between_insights_emails==0:
        send_basic_insights_email(insights_email_hours_back,user_email,user)

    ### Step 7.
    if loop_number%hours_between_bugreport_emails==0:
        send_bug_report_email(bugreport_email_hours_back,dev_email,user)
    
    ### In case the loop is fully executed, we fire a log that sums-up the success of each function of the loop
    dataAPI().log(user,"MAIN","INFO",'loop {} executed, successes : [update_followers_data : {}, unfollow_accounts : {}, update_follow_actions_data:{}, explore_hashtag : {}]'.format(loop_number,success1,success2,success3,success4))
    
    ### We want the while(1) loop content to run approx. every hour
    dataAPI().log(user,"MAIN","INFO","time to wait approx. 1 hour before the next loop")
    smart_sleep(3400)
    
    loop_number+=1
    
    
    
    

 
    
    
    
    
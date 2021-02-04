#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings 
from time import sleep
import random
from sys import argv
import datetime
import numpy as np
warnings.filterwarnings("ignore") #f**k warnings
from utilities import load_config_user,load_config_variable
from instabot_functions import log_in,update_followers_data,unfollow_accounts,update_follow_actions_data,follow_accounts_from_hashtag,follow_first_followers,generate_daily_poisson_times
from instabot_email_service import send_basic_insights_email,send_bug_report_email
from instabot_data_api import dataAPI
import instabot_data_api
instabot_data_api.STORE_LOGS = True 
headless = True

user = argv[1]
config_file_path = argv[2]

############################################# General configuration ###################################
scraper_account_email_address = load_config_variable("SCRAPER_ACCOUNT_GMAIL_ADDRESS","config.json")
scraper_account_password = load_config_variable("SCRAPER_ACCOUNT_PASSWORD","config.json")
#######################################################################################################


############################################# Configuration bit for the user ###########################
variables = ["user_email","user_password","hashtags","account_usernames","dev_email"]
config = load_config_user(user,variables,config_file_path)
user_email = config["user_email"]
user_password = config["user_password"]
account_usernames = config["account_usernames"]
hashtags = config["hashtags"]
dev_email = config["dev_email"]
##########################################################################################################


### TEST
# user = "edouardthegourmet"
# headless = True


nb_actions_per_day = 30

while(1):
    ## The bot sleeps until 7am
    now = datetime.datetime.now()
    if now.hour >= 0 and now.hour < 7:
        seconds_to_sleep = (8 - now.hour)*3600 - (now.minute)*60
        dataAPI().log(user,"MAIN","INFO","It's night time, time for the bot to sleep : approximately {} seconds".format(seconds_to_sleep))
        sleep(seconds_to_sleep)   
        ### Sleep a bit more so that the bot starts randomly between 7 and 9 am  (on average at 8)
        sleep(random.randint(0,7200))
    
    ### define the start and stop timestamps for the day
    dataAPI().log(user,"MAIN","INFO","Good morning ! The bot started for user {} !".format(user))
    start_day = datetime.datetime.now()
    stop_day = start_day + datetime.timedelta(hours=16,seconds = random.randint(-3600,3600))
    
    ### generate randomly the instant at which the bot will perform its actions
    times = generate_daily_poisson_times(start_day,stop_day,nb_actions_per_day)
    
    ### Send the morning emails
    # send_basic_insights_email(24,user_email,user)
    # send_bug_report_email(12,dev_email,user)
    
    option = 1
    ### REMINDER : every option will execute 6 times per day on average
    for time in times:
        if datetime.datetime.now() < time:
            sleep((time-datetime.datetime.now()).seconds)
        if option == 1:
            dataAPI().log(user,"MAIN","INFO","Option 1 started")
            driver = log_in(scraper_account_email_address,scraper_account_password,user,headless=headless)            
            ok = update_followers_data(user,driver)
            driver.close()
            dataAPI().log(user,"MAIN","INFO","Option 1 ended - success={}".format(ok))
        if option == 2:
            dataAPI().log(user,"MAIN","INFO","Option 2 started")
            driver = log_in(scraper_account_email_address,scraper_account_password,user,headless=headless)
            ok = update_follow_actions_data(user,driver)
            driver.close()
            dataAPI().log(user,"MAIN","INFO","Option 2 ended - success={}".format(ok)) 
        if option == 3:
            dataAPI().log(user,"MAIN","INFO","Option 3 started")
            driver = log_in(user_email,user_password,user,for_aws=False,headless=headless)
            nb_max_accounts_to_unfollow = 6
            ok = unfollow_accounts(nb_max_accounts_to_unfollow,user,driver)
            driver.close()
            dataAPI().log(user,"MAIN","INFO","Option 3 ended - success={}".format(ok))       
        if option == 4:
            dataAPI().log(user,"MAIN","INFO","Option 4 started")
            driver = log_in(user_email,user_password,user,use_cookies=True,for_aws=False,headless=headless)
            nb_follows_per_hashtag = np.random.choice([3,4,5]) 
            hashtag = hashtags[np.random.randint(0,len(hashtags))]
            ok = follow_accounts_from_hashtag(hashtag,user=user,
                                               nb_follows=nb_follows_per_hashtag,
                                               driver=driver)            
            driver.close()
            dataAPI().log(user,"MAIN","INFO","Option 4 ended - success={}".format(ok))            
        if option == 5:
            dataAPI().log(user,"MAIN","INFO","Option 5 started")
            driver = log_in(user_email,user_password,user,for_aws=False,headless=headless)
            nb_follows = np.random.choice([2,3,4,5])
            account_username = account_usernames[np.random.randint(0,len(account_usernames))]
            ok = follow_first_followers(account_username,nb_follows,user,driver)
            driver.close()
            dataAPI().log(user,"MAIN","INFO","Option 5 ended - success={}".format(ok)) 
            
        next_option = random.randint(1,5)
        if next_option == option:
            next_option = (next_option+1)%5
        option = next_option
    
    ### Send the evening emails        
    # send_basic_insights_email(24,user_email,user)
    # send_bug_report_email(12,dev_email,user)
        
    dataAPI().log(user,"MAIN","INFO","Loop over :)")        
    

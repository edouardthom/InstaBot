#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings 
warnings.filterwarnings("ignore") #f**k warnings
import datetime

from instabot_functions import log_in,update_followers_data,unfollow_accounts,update_follow_actions_data,follow_accounts_from_hashtag,sleep,datetime,np
from instabot_email_service import send_basic_insights_email,send_bug_report_email
from instabot_data_api import dataAPI
from instabot_run_variables import *
import instabot_data_api

instabot_data_api.STORE_LOGS = True 




### That loop runs once every [time_between_loops] seconds
last_iteration = datetime.datetime.now()
loop_number = 0
dataAPI().log(user,"MAIN","INFO","Bot started for user {} !".format(user))
while 1:
    dataAPI().log(user,"MAIN","INFO","loop {} start".format(loop_number))
    
    driver = log_in(user_email,password,user,for_aws=False,headless=False)
    
    ### If login failure, we cannot pursue the loop, we retry
    if driver==0:
        dataAPI().log(user,"MAIN","INFO","failed to log-in and get the driver - restarting in 2 minutes...")
        sleep(120)
        continue
    
    success1 = update_followers_data(user,driver)
    
    success2 = unfollow_accounts(user,driver)
    
    success3 = update_follow_actions_data(user,driver)
    
    success4 = []
    for _ in range(nb_hashtags_per_loop):
        hashtag = hashtags[np.random.randint(0,len(hashtags))]
        success = follow_accounts_from_hashtag(hashtag,user=user,
                                                 nb_follows=nb_follows_per_hashtag,driver=driver)
        success4.append(success)
    driver.close()
    
    ### Insights email sending
    if loop_number%max(1,int(time_between_insights_emails/time_between_loops))==0:
        send_basic_insights_email(email_hours_back,user_email,user)

    ### Bug report email sending
    if loop_number%max(1,int(time_between_maintenance_emails/time_between_loops))==0:
        send_bug_report_email(email_hours_back,dev_email,user)
    
    ### In case the loop is fully executed, we fire a log that sums-up the success of each function of the loop
    dataAPI().log(user,"MAIN","INFO",'loop {} executed, successes : [update_followers_data : {}, unfollow_accounts : {}, update_follow_actions_data:{}, explore_hashtag : {}]'.format(loop_number,update_followers_success,unfollowing_output,explore_hashtag_outputs))
    
    ### We want the while(1) loop content to run every hour
    while datetime.datetime.now() < last_round + datetime.timedelta(seconds = time_between_loops):
        time_to_wait = str((last_round + datetime.timedelta(hours = 1) - datetime.datetime.now()).seconds)
        dataAPI().log(user,"MAIN","INFO","heartbeak... time to wait : {}".format(time_to_wait))
        sleep(int(time_between_loops/10)) 
    last_iteration = datetime.datetime.now()
    loop_number+=1
    
    
    
    
    
    
    
    
 
    
    
    
    
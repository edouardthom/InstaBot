#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings 
warnings.filterwarnings("ignore") #f**k warnings

from instabot_functions import log_in,update_followers_data,unfollow_accounts,update_follow_actions_data,follow_accounts_from_hashtag,sleep,datetime,np
from instabot_email_service import send_basic_insights_email,send_bug_report_email
from instabot_data_api import dataAPI
from instabot_run_variables import user,user_email,user_password,hashtags,time_between_loops,nb_hashtags_per_loop,nb_follows_per_hashtag
from instabot_run_variables import time_between_insights_emails,dev_email,time_between_bugreport_emails,bugreport_email_hours_back,insights_email_hours_back

import instabot_data_api

instabot_data_api.STORE_LOGS = True 




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
last_iteration = datetime.datetime.now()
loop_number = 0
dataAPI().log(user,"MAIN","INFO","Bot started for user {} !".format(user))
while 1:
    dataAPI().log(user,"MAIN","INFO","loop {} start".format(loop_number))
    
    ### Step 1.
    driver = log_in(user_email,user_password,user,for_aws=False,headless=True)
    
    ### If login failure, we cannot pursue the loop, we retry
    if driver==0:
        dataAPI().log(user,"MAIN","INFO","failed to log-in and get the driver - restarting in 2 minutes...")
        sleep(120)
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
                                                 nb_follows=nb_follows_per_hashtag,driver=driver)
        success4.append(success)
    driver.close()
    
    ### Step 6.
    if loop_number%max(1,int(time_between_insights_emails/time_between_loops))==0:
        send_basic_insights_email(insights_email_hours_back,user_email,user)

    ### Step 7.
    if loop_number%max(1,int(time_between_bugreport_emails/time_between_loops))==0:
        send_bug_report_email(bugreport_email_hours_back,dev_email,user)
    
    ### In case the loop is fully executed, we fire a log that sums-up the success of each function of the loop
    dataAPI().log(user,"MAIN","INFO",'loop {} executed, successes : [update_followers_data : {}, unfollow_accounts : {}, update_follow_actions_data:{}, explore_hashtag : {}]'.format(loop_number,success1,success2,success3,success4))
    ### We want the while(1) loop content to run every hour
    while datetime.datetime.now() < last_iteration + datetime.timedelta(seconds = time_between_loops):
        time_to_wait = str((last_iteration + datetime.timedelta(hours = 1) - datetime.datetime.now()).seconds)
        dataAPI().log(user,"MAIN","INFO","heartbeak... time to wait : {}".format(time_to_wait))
        sleep(int(time_between_loops/10)) 
    last_iteration = datetime.datetime.now()
    loop_number+=1
    
    
    
    
    
    
    
    
 
    
    
    
    
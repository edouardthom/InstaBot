#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from instabot_functions import log_in,update_followers,unfollowing_of_accounts_followed_by_bot,explore_hashtag,sleep,datetime,np
from instabot_email_service import send_basic_insights_email
import warnings 
warnings.filterwarnings("ignore") #f**k warnings
import instabot_data_api
from instabot_data_api import dataAPI
instabot_data_api.STORE_LOGS = True 
from instabot_run_variables import time_between_loops,nb_hashtags_per_loop,nb_follows_per_hashtag,user,email,password,hashtags,email_hours_back,time_between_emails





### That loop runs once every time_between_loops seconds
last_round = datetime.datetime.now()
loop_number = 0
while 1:
    dataAPI().log(user,"MAIN","INFO","loop {} start".format(loop_number))
    
    driver = log_in(email,password,user,for_aws=False,headless=True)
    ### If login failure, we cannot pursue the loop, we retry
    if driver==0:
        dataAPI().log(user,"MAIN","INFO","failed to log-in and get the driver - restarting in 2 minutes...")
        sleep(120)
        continue
    
    update_followers_output = update_followers(user,driver)
    
    unfollowing_output = unfollowing_of_accounts_followed_by_bot(user,driver)
 
    explore_hashtag_outputs = []
    for _ in range(nb_hashtags_per_loop):
        hashtag = hashtags[np.random.randint(0,len(hashtags))]
        explore_hashtag_output = explore_hashtag(hashtag,user=user,
                                                 nb_follows=nb_follows_per_hashtag,driver=driver)
        explore_hashtag_outputs.append(explore_hashtag_output)
    driver.close()
    
    ### Email sending
    if loop_number%max(1,int(time_between_emails/time_between_loops))==0:
        send_basic_insights_email(email_hours_back,email,user)
    
    ### In case the loop is fully executed, we fire a log that sums-up the success of each function of the loop
    dataAPI().log(user,"MAIN","INFO",'loop {0} executed, success : [update_followers : {1}, unfollowing_of_bot_followed_users : {2}, explore_hashtag : {3}]'.format(loop_number,update_followers_output,unfollowing_output,explore_hashtag_outputs))
    
    ### We want the while(1) loop content to run every hour
    while datetime.datetime.now() < last_round + datetime.timedelta(seconds = time_between_loops):
        time_to_wait = str((last_round + datetime.timedelta(hours = 1) - datetime.datetime.now()).seconds)
        dataAPI().log(user,"MAIN","INFO","heartbeak... time to wait : {}".format(time_to_wait))
        sleep(int(time_between_loops/10)) 
    last_round = datetime.datetime.now()
    loop_number+=1
    
    
    
    
    
    
    
    
 
    
    
    
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from instabot_functions import log_in,update_followers,unfollowing_of_bot_followed_users,explore_hashtag,sleep,datetime,np
import warnings 
warnings.filterwarnings("ignore") #f**k warnings
import instabot_data_api
from instabot_data_api import dataAPI



####################################################################################
############################ RUN VARIABLES - TO FILL ###############################
####################################################################################
instabot_data_api.STORE_LOGS = True 
time_between_loops = 3600  
nb_hashtags_per_loop = 3   
nb_follows_per_hashtag = 4
    
user = "edouard_thom"
email = 'edouard.thom@gmail.com'
password = ''

hashtags = ["instalife","friends","beach","ski","followeraktif","follower4follower",
            "instagood","followme","selfie","foodie",
            "car","clothing","followers","like4like","f2f","l4l"]
####################################################################################
####################################################################################
####################################################################################




last_round = datetime.datetime.now()
while 1:
    dataAPI().log(user,"MAIN","INFO","loop start")
    
    driver = log_in(email,password,user,for_aws=False)
    ### If login failure, we cannot pursue the loop, we retry
    if driver==0:
        dataAPI().log(user,"MAIN","INFO","failed to log-in and get the driver - restarting in 2 minutes...")
        sleep(120)
        continue
    
    update_followers_output = update_followers(user,driver)
    
    unfollowing_output = unfollowing_of_bot_followed_users(user,driver)
 
    explore_hashtag_outputs = []
    for _ in range(nb_hashtags_per_loop):
        hashtag = hashtags[np.random.randint(0,len(hashtags))]
        explore_hashtag_output = explore_hashtag(hashtag,user=user,
                                                 nb_follows=nb_follows_per_hashtag,driver=driver)
        explore_hashtag_outputs.append(explore_hashtag_output)
    driver.close()
    
    ### In case the loop is fully executed, we fire a log that sums-up the success of each function of the loop
    dataAPI().log(user,"MAIN","INFO","loop executed, outputs : [update_followers : {0}, unfollowing_of_bot_followed_users : {1}, explore_hashtag : {2}]".format(update_followers_output,unfollowing_output,explore_hashtag_outputs))
    
    ### We want the while1 loop content to run every hour
    while datetime.datetime.now() < last_round + datetime.timedelta(hours = 1):
        time_to_wait = str((last_round + datetime.timedelta(hours = 1) - datetime.datetime.now()).seconds)
        dataAPI().log(user,"MAIN","INFO","heartbeak... time to wait : {}".format(time_to_wait))
        sleep(600)
        
    last_round = datetime.datetime.now()
 
    
    
    
    
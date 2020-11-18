#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from instabot_functions import *
from instabot_prepare_data_for_plot import *
import warnings 

warnings.filterwarnings("ignore") #f**k warnings




user = "edouard_thom"
username = 'edouard.thom@gmail.com'
password = 'pro-accent!0k&'
hashtags = ["instalife","friends","beach","ski","followeraktif","follower4follower",
            "instagood","followme","selfie","foodie",
            "car","clothing","followers","like4like","f2f","l4l"]



last_round = datetime.datetime.now()
while 1:
    print("Right now : "+last_round.strftime("%m/%d/%Y, %H:%M:%S"))
    driver = log_in(username,password,for_aws=False)
    sleep(3)
    
    update_followers(user,driver)
    last_update_followers = datetime.datetime.now()
    sleep(3)
    
    unfollowing_of_bot_followed_users(user,driver)
    last_unfollowing_round = datetime.datetime.now()
    sleep(3)
 
    nb_follows_per_hashtag = 4
    for _ in range(3):
        hashtag = hashtags[np.random.randint(0,len(hashtags))]
        explore_hashtag(hashtag,user=user,nb_follows=nb_follows_per_hashtag,driver=driver)
    
    driver.close()
    
    print("Time to wait...")
    ### We want the while1 loop content to run every hour
    while datetime.datetime.now() < last_round + datetime.timedelta(hours = 1):
        time_to_wait = str((last_round + datetime.timedelta(hours = 1) - datetime.datetime.now()).seconds)
        print("{} seconds to wait...".format(time_to_wait))
        sleep(60)
        
    last_round = datetime.datetime.now()






  
    
    

    
    
    
    
    

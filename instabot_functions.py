#!/usr/bin/env python3

from instabot_data_api import dataAPI
from instabot_ui_api import UIComponentsAPI
from utilities import smart_sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import datetime
import pandas as pd
import traceback
import numpy as np   
import random
import math

############################################################################################################
############################# The 5 Main independent blocks #############################################
############################################################################################################

def open_browser(user,for_aws=False,headless=False):
    """
    Just opens a browser and Instagram, but doesn't log-in'

    """
    dataAPI().log(user,"open_browser","INFO","start") 
    try:
        if for_aws:
            chrome_options = Options()
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(chrome_options=chrome_options)
        else:
            if headless:
                chrome_options = Options()
                chrome_options.add_argument('headless')
                driver = webdriver.Chrome(chrome_options=chrome_options)
            else:
                driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
        driver.get("https://www.instagram.com/")
        UIComponentsAPI().click("login_accept_cookies",user,driver)
        dataAPI().log(user,"open_browser","INFO","success - browser opened") 
        return driver
    except:
        dataAPI().log(user,"log_in","ERROR","failed, full exception : {}".format(traceback.format_exc()))  
        smart_sleep(3)
        return 0


def log_in(email,password,user,for_aws=False,headless=False):
    """
    This function creates a webdriver, and log-in into Instagram for the specified user.
    It returns the webdriver for performing further actions.

    """
    dataAPI().log(user,"log_in","INFO","start") 
    try:
        if for_aws:
            chrome_options = Options()
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(chrome_options=chrome_options)
        else:
            if headless:
                chrome_options = Options()
                chrome_options.add_argument('headless')
                driver = webdriver.Chrome(chrome_options=chrome_options)
            else:
                driver = webdriver.Chrome()
        
        driver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        
        UIComponentsAPI().click("login_accept_cookies",user,driver)
        step1 = UIComponentsAPI().enter_text("login_email_input_field",email,user,driver)
        step2 = UIComponentsAPI().enter_text("login_password_input_field",password,user,driver) 
        step3 = UIComponentsAPI().click("login_connexion_button",user,driver)
        
        if step1+step2+step3<3:
            dataAPI().log(user,"log_in","ERROR","failed") 
            return 0
        else:
            dataAPI().log(user,"log_in","INFO","success")  
            smart_sleep(3)
            return driver
    except:
        dataAPI().log(user,"log_in","ERROR","failed, full exception : {}".format(traceback.format_exc()))  
        smart_sleep(3)
        return 0


def update_followers_data(user,driver):
    dataAPI().log(user,"update_followers","INFO","start")
    try:
        profile_url = 'https://www.instagram.com/{}/'.format(user)
        if driver.current_url!=profile_url:
            driver.get(profile_url)
        smart_sleep(2)
        
        followers_now = get_followers_following_for_user("followers",user,driver)

        if type(followers_now) == int :
            dataAPI().log(user,"update_followers","ERROR","failed to get the followers list -> abort the followers update")
            return 0
        
        followers_now = pd.DataFrame({"present_now":[1]*len(followers_now),
                                      "account_username":followers_now})
        
        ### Update the followers dataframe for that user
        data = dataAPI().get("followers",user)
        data = data.merge(followers_now,how="outer",on="account_username")
        data["unfollow_time"][(data.present_now.isnull())
                              &(data.unfollow_time.isnull())] = datetime.datetime.now()
        data["unfollow_time"][(data.present_now==1)
                              &(~data.unfollow_time.isnull())] = None
        data = data.fillna({"follow_time":datetime.datetime.now()})
        data = data.drop("present_now",1)
        dataAPI().store("followers",user,data)
        dataAPI().log(user,"update_followers","INFO","success")
        smart_sleep(3)
        return 1
    except:
        dataAPI().log(user,"update_followers","ERROR","UNIDENTIFIED failure, full exception : {}".format(traceback.format_exc())) 
        smart_sleep(3)
        return 0
    


def unfollow_accounts(nb_max_accounts_to_unfollow,user,driver):
    try:
        dataAPI().log(user,"unfollow_accounts","INFO","start")
        
        ### Get the follows made by the bot
        follow_actions = dataAPI().get("follow_actions",user)
        
        ### Identify the accounts that the bot followed that need to be unfollowed because their time has come 
        # Reminder : In the function explore_hashtag, each account followed by the bot is assigned a number of hours before the unfollow must happen
        follow_actions['follow_time'] = follow_actions['follow_time'].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f"))
        follow_actions["planned_unfollow_date"] = follow_actions["follow_time"] + follow_actions.hours_before_unfollowing.apply(lambda x:datetime.timedelta(hours=x))
        accounts_to_unfollow = follow_actions[(follow_actions.planned_unfollow_date<=datetime.datetime.now())
                                             &(follow_actions.unfollow_time.isnull())]
        accounts_to_unfollow = accounts_to_unfollow.account_username
        if len(accounts_to_unfollow)==0:
            dataAPI().log(user,"unfollow_accounts","INFO","no accounts to unfollow")
            return 1
        
        ### Then we (try to) unfollow these accounts
        dataAPI().log(user,"unfollow_accounts","INFO","{} accounts to unfollow...".format(str(len(accounts_to_unfollow))))
        nb_of_accounts_unfollowed = 0
        smart_sleep(2)
        for u in accounts_to_unfollow.iloc[:nb_max_accounts_to_unfollow]:
            smart_sleep(5)
            unfollowing_success = unfollow_one_account(u,user,driver)
            nb_of_accounts_unfollowed+=unfollowing_success
        # remark : we can fail to unfollow an account because we were not following it. (the bot is not the only entity to have the ability to unfollow accounts)
        dataAPI().log(user,"unfollow_accounts","INFO","{} accounts successfully unfollowed".format(nb_of_accounts_unfollowed))
        return 1
    except:
        dataAPI().log(user,"unfollow_accounts","ERROR","UNIDENTIFIED failure, full exception : {}".format(traceback.format_exc())) 
        smart_sleep(3)
        return 0           


def update_follow_actions_data(user,driver):
    try:
        ### Get the follows made by the bot
        follow_actions = dataAPI().get("follow_actions",user)
        follow_actions['follow_time'] = follow_actions['follow_time'].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f"))
        follow_actions["planned_unfollow_date"] = follow_actions["follow_time"] + follow_actions.hours_before_unfollowing.apply(lambda x:datetime.timedelta(hours=x))

        ### We get the list of accounts followed by the user to update the follow data
        profile_url = 'https://www.instagram.com/{}/'.format(user)
        driver.get(profile_url)
        following = get_followers_following_for_user("following",user,driver)
    
        if type(following) ==int : 
            dataAPI().log(user,"update_follow_actions_data","ERROR","failed to get the following list -> stop the function execution")
            smart_sleep(3)
            return 0
            
        following = pd.DataFrame({"account_username":following,"following":1})
        follow_actions = follow_actions.merge(following,on="account_username",how="left")
        nb_new_unfollowings = ((follow_actions.following.isnull())&
                               (follow_actions["unfollow_time"].isnull())).sum()
        dataAPI().log(user,"update_follow_actions_data","INFO",'{} accounts stopped being followed since last time the dataframe follow_actions was updated'.format(nb_new_unfollowings))
        
        (follow_actions["unfollow_time"])[(follow_actions.following.isnull())
                                      &(follow_actions["unfollow_time"].isnull())] = datetime.datetime.now()
        follow_actions = follow_actions.drop("following",1)
        follow_actions = follow_actions.drop("planned_unfollow_date",1)
        dataAPI().store("follow_actions",user,follow_actions)
        dataAPI().log(user,"update_follow_actions_data","INFO","follow_actions dataframe for user {} successfully updated".format(user))
        smart_sleep(3)
        return 1
    except:
        dataAPI().log(user,"update_follow_actions_data","ERROR","UNIDENTIFIED failure, full exception : {}".format(traceback.format_exc())) 
        smart_sleep(3)
        return 0        


    
def follow_first_followers(account_username,nb_follows,user,driver):
    dataAPI().log(user,"follow_first_followers","INFO","start for account {}".format(account_username))  
    
    ### 1 - access account page
    account_url = "https://www.instagram.com/"+account_username+"/"
    try:
        driver.get(account_url)
    except:
        dataAPI().log(user,"follow_first_followers","ERROR","couldn't access account page") 
        return 0
    smart_sleep(2)
    
    ### 2 - open the list of followers of the account
    try:
        nb_followers = UIComponentsAPI().get_text_and_click("profile_page_followers_button",user,driver)
        nb_followers = treat_number(nb_followers,user)
    except:
        dataAPI().log(user,"follow_first_followers","ERROR","couldn't access followers list")  
        return 0
    smart_sleep(5)
    
    ### 3 - follow some of the account's followers
    nb_follows = min(nb_follows,nb_followers)
    dataAPI().log(user,"follow_first_followers","INFO","Let's follow {} of the account's followers".format(nb_follows))
    nb_accounts_followed = 0
    fails = 0
    n = 2
    while (nb_accounts_followed < nb_follows) and (fails<3):
        try:
            xpath = "/html/body/div[5]/div/div/div[2]/ul/div/li[{}]/div/div[2]/div[1]/div/div/span/a".format(n)
            target_username = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,xpath))).text.split("\n")[0]
        except:
            dataAPI().log(user,"follow_first_followers","ERROR","couldn't get username for follower account number {}".format(n))
            fails += 1
            n+=1
            smart_sleep(3)
            continue             
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        smart_sleep(2)
        account_info = get_account_data_and_follow(target_username,user,driver)
        smart_sleep(2)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        smart_sleep(2)
        
        if len(account_info) == 0:
            dataAPI().log(user,"follow_first_followers","ERROR","couldn't follow + get data for follower account number {}".format(n))
            fails += 1
            n+=1
            continue 
 
        ### We log the follow
        record = {"follow_time" : datetime.datetime.now(),
                  "account_username" : account_info[0],
                  "account_name" : account_info[1],
                  "account_nb_followers" : account_info[2],
                  "account_nb_following" : account_info[3],
                  "account_nb_posts" : account_info[4],
                  "account_description" : account_info[5],
                  "account_nb_likes_per_post" : account_info[6],
                  "account_source" : "follow_first_followers", 
                  "account_source_attributes" : {"account" : account_username},
                  "first_pic_liked" : 0,
                  "hours_before_unfollowing" : np.random.randint(2,24,1)[0],
                  "unfollow_time" : None}        
        dataAPI().add_record("follow_actions",user,record)
        nb_accounts_followed+=1
        n+=1
        dataAPI().log(user,"follow_first_followers","INFO","successfully followed account {}".format(target_username))
        smart_sleep(10)
    dataAPI().log(user,"follow_first_followers","INFO","end - {} accounts followed".format(nb_accounts_followed))  

            
    
def follow_accounts_from_hashtag(hashtag,nb_follows,user,driver):
    dataAPI().log(user,"explore_hashtag","INFO","start, #{}".format(hashtag))  
    
    driver.get('https://www.instagram.com/explore/tags/'+ hashtag + '/')
    smart_sleep(2)
    ok = UIComponentsAPI().click("first_thumbnail_photo",user,driver)
    if ok==0:
        dataAPI().log(user,"explore_hashtag","ERROR","fail, full exception : {}".format(traceback.format_exc()))  
        smart_sleep(3)
        return 0
        
    pic_number = 0
    nb_accounts_followed = 0
    failures = 0
    while nb_accounts_followed < nb_follows:
        
        ### In each iteration : 3 main steps that can fail :
        # - step 1 : getting the account name
        # - step 2 : getting the account details (number of posts, followers,...)
        # - step 3 : follow the account
        # Whenever 1 of these fail, we try to move to the next picture (press_right_arrow)
        # If the press fails, we are doomed : we just stop the loop (break), and therefore the whole function
        # If the press succeeds, we go to the next iteration (continue), and we log 1 fail (failures+=1)
        # After 4 fails, we just give up and end the loop.
        if failures>=6:
            dataAPI().log(user,"explore_hashtag","ERROR","Too many failures, we stop the loop")
            break
        
        ### Step 1
        account_username = UIComponentsAPI().get_text("picture_carousel_account_name",user,driver)
        if account_username==0:
            right_arrow_pressed = press_righ_arrow(pic_number,user,driver)
            if right_arrow_pressed == 0:
                dataAPI().log(user,"explore_hashtag","ERROR","stop the processing of hashtag {}".format(hashtag))
                break
            failures+=1
            continue
        dataAPI().log(user,"explore_hashtag","INFO","start processing for account : {}".format(account_username))
        
        ### Step 2
        account_url = "https://www.instagram.com/"+account_username+"/"
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(account_url)        
        account_info = get_account_data_from_profile_page(user,driver)   
        if len(account_info)==0:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            right_arrow_pressed = press_righ_arrow(pic_number,user,driver)
            if right_arrow_pressed == 0:
                dataAPI().log(user,"explore_hashtag","ERROR","stop the processing of hashtag {}".format(hashtag))
                break
            failures+=1
            continue
        
        ### Step 3
        follow_success = follow_one_account_from_profile_page(account_username,user,driver)  
        if follow_success==0:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            right_arrow_pressed = press_righ_arrow(pic_number,user,driver)
            if right_arrow_pressed == 0:
                dataAPI().log(user,"explore_hashtag","ERROR","stop the processing of hashtag {}".format(hashtag))
                smart_sleep(2)
                break
            pic_number+=1
            failures+=1
            smart_sleep(2)
            continue
        dataAPI().log(user,"explore_hashtag","INFO","successfully followed account : {}".format(account_username))

        ### The 3 steps succeeded, lets' move to the less important bits 
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
         
        first_pic_liked = 0
        if np.random.randint(2):
            first_pic_liked = UIComponentsAPI().click("pictures_carousel_like_button",user,driver)
        
        ### IMPORTANT VARIABLE : number of hours max before unfollowing !
        ### The bot follows each accounts for a random limited amount of hours - between 2 and 24 hours.
        record = {"follow_time" : datetime.datetime.now(),
                  "account_username" : account_info[0],
                  "account_name" : account_info[1],
                  "account_nb_followers" : account_info[2],
                  "account_nb_following" : account_info[3],
                  "account_nb_posts" : account_info[4],
                  "account_description" : account_info[5],
                  "account_nb_likes_per_post" : account_info[6],
                  "account_source" : "follow_accounts_from_hashtag", 
                  "account_source_attributes" : {"hashtag" : hashtag},
                  "first_pic_liked" : first_pic_liked,
                  "hours_before_unfollowing" : np.random.randint(2,24,1)[0],
                  "unfollow_time" : None}
        dataAPI().add_record("follow_actions",user,record)
        nb_accounts_followed+=1
        smart_sleep(10)
        
        success_right_arrow_press = press_righ_arrow(pic_number,user,driver)
        if success_right_arrow_press==0:
            dataAPI().log(user,"explore_hashtag","ERROR","stop the processing of hashtag {}".format(hashtag))
            smart_sleep(2)
            break
        pic_number=1
        
    
    dataAPI().log(user,"explore_hashtag","INFO","hashtag {0} processed, {1} accounts followed".format(hashtag,nb_accounts_followed))
    smart_sleep(3)
    return 1
        

############################################################################################################
################################## Secondary interaction functions #########################################
############################################################################################################



def get_followers_following_for_user(entry,user,driver):
    nb_max_attempts = 3
    attempt = 1
    dataAPI().log(user,"get_followers_following_for_user","INFO","start - first attempt to get the {} data".format(entry))
    while attempt <= nb_max_attempts:
        smart_sleep(2)
        entries,nb_entries = get_followers_following_for_user_one_try(entry,user,driver)
        if entries==0:
            attempt+=1
            continue
        elif (len(entries)<nb_entries-1):
            attempt+=1
            continue
        else:
            dataAPI().log(user,"get_followers_following_for_user","INFO","success at attempt number : {}".format(attempt))
            return entries
    dataAPI().log(user,"get_followers_following_for_user","ERROR","failed after {} attempts".format(nb_max_attempts))
    smart_sleep(2)
    return 0
       
def get_followers_following_for_user_one_try(entry,user,driver):
    """
    This function opens the user profile page, and the scrollable window of followers or following, according to the 
    entry paramener ("followers" or "following")
    """
    dataAPI().log(user,"get_followers_following_for_user_one_try","INFO","start")
    try:
        profile_url = 'https://www.instagram.com/{}/'.format(user)
        driver.get(profile_url)
        smart_sleep(2)
    except:
        dataAPI().log(user,"get_followers_following_for_user_one_try","ERROR","couldn't load user profile page")
        smart_sleep(2)
        return (0,0)
    ### Open the followers/ing scrollable window from the profile page + get the # of entries
    if entry == "followers":
        nb_entries = UIComponentsAPI().get_text_and_click("profile_page_followers_button",user,driver)
    else:
        nb_entries = UIComponentsAPI().get_text_and_click("profile_page_following_button",user,driver)
    if nb_entries==0:
        return (0,0)
    smart_sleep(1)
    try:
        nb_entries = treat_number(nb_entries,user)
        #find all elements in list
        fBody_xpath = "//div[@class='isgrP']"    
        fBody = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, fBody_xpath)))
        
        scroll = 0
        while scroll < nb_entries: # each scroll displays ~12 row, we divide by 3 to be reaaaallllyyy sure we don't miss any
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
            smart_sleep(1)
            scroll += 1
        
        entries = []
        fails = 0
        smart_sleep(2)
        for n in range(1,nb_entries+1):
            if fails>=2:
                dataAPI().log(user,"get_followers_following_for_user_one_try","ERROR","too many fails to get the entries, stopping execution")
                return (0,0)
            try:
                xpath = "/html/body/div[5]/div/div/div[2]/ul/div/li[{}]".format(n)
                info = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,xpath))).text
                name = info.split("\n")[0]
                entries.append(name)
                smart_sleep(0.5)
            except:
                fails+=1
                dataAPI().log(user,"get_followers_following_for_user_one_try","ERROR","couldn't get entry {}".format(n))
                smart_sleep(0.5)
                pass

        dataAPI().log(user,"get_followers_following_for_user_one_try","INFO","{} entries scraped : {}/{}".format(entry,len(entries),nb_entries))
        smart_sleep(2)
        return (entries,nb_entries)
    
    except:
        dataAPI().log(user,"get_followers_following_for_user_one_try","ERROR","UNIDENTIFIED failure, full exception : {}".format(traceback.format_exc())) 
        smart_sleep(2)
        return (0,0)



def unfollow_one_account(user_to_unfollow,user,driver):
    dataAPI().log(user,"unfollow_account_from_profile_page","INFO","start, user_to_unfollow={}".format(user_to_unfollow))
    ### Sometimes the unfollow fails even if the right buttons are clicked according to stupid Selenium...
    # So we have to check if the account is effectively unfollowed. If not re retry in the limit of 2 fails.
    fails = 0
    while fails <= 2:
        dataAPI().log(user,"unfollow_account_from_profile_page","INFO","trying to unfollow.. {} tries so far".format(fails))
        try:
            driver.get('https://www.instagram.com/{}/'.format(user_to_unfollow))
        except:
            dataAPI().log(user,"unfollow_account_from_profile_page","ERROR","failed to access profile URL")
            fails+=1
            continue
       
        status = UIComponentsAPI().get_text("profile_page_follow_status_button",user,driver)
        print("Status is {}".format(status))
        if status=="Follow":
            dataAPI().log(user,"unfollow_account_from_profile_page","INFO","this account is not followed... stop")
            return 0
        
        smart_sleep(2)
        ok = UIComponentsAPI().click("unfollow_button",user,driver)
        if ok==0:
            dataAPI().log(user,"unfollow_account_from_profile_page","ERROR","Failed to unfollow user {} - 1st unfollow click".format(user_to_unfollow))
            fails+=1
            continue
        smart_sleep(2)
        if UIComponentsAPI().click("unfollow_red_button_confirm",user,driver):
            smart_sleep(4)
            driver.get('https://www.instagram.com/{}/'.format(user_to_unfollow))
            ### Officially the unfollow has been confirmed, but we need to double check...
            status = UIComponentsAPI().get_text("profile_page_follow_status_button",user,driver)
            print("Status is {}".format(status))
            if status == "Follow": ### Which means we are not following the guy anymore :)
                dataAPI().log(user,"unfollow_account_from_profile_page","INFO","success, account {} unfollowed".format(user_to_unfollow))
                return 1
            else:
                dataAPI().log(user,"unfollow_account_from_profile_page","INFO","still not unfollowed, we try again...")
                fails+=1
                continue
        else:
            dataAPI().log(user,"unfollow_account_from_profile_page","ERROR","Failed to unfollow user {} - 2nd unfollow click".format(user_to_unfollow))
            fails+=1
            continue

    dataAPI().log(user,"unfollow_account_from_profile_page","ERROR","(probably) failed to unfollow user {}...".format(user_to_unfollow))
    return 0







    
def press_righ_arrow(pic_number,user,driver):
    if pic_number==0:
        return UIComponentsAPI().click("pictures_carousel_first_pic_right_arrow",user,driver)
    else:
        return UIComponentsAPI().click("pictures_carousel_not_first_pic_right_arrow",user,driver)








def get_account_data_and_follow(account_name,user,driver):
    dataAPI().log(user,"get_account_data_and_follow","INFO","start")
    account_url = "https://www.instagram.com/"+account_name+"/"
    try:
        driver.get(account_url)
    except:
        dataAPI().log(user,"follow_first_followers","ERROR","couldn't access account page")  
    smart_sleep(2)
    info = get_account_data_from_profile_page(user,driver)
    smart_sleep(1)
    step_2 = follow_one_account_from_profile_page(account_name,user,driver)
    smart_sleep(2)
    if (len(info)>0) and step_2==1:
        dataAPI().log(user,"follow_first_followers","INFO","successfully stored account information and followed {}".format(account_name))  
        return info
    else:
        dataAPI().log(user,"follow_first_followers","INFO","failed for {}".format(account_name))  
        return []

def follow_one_account_from_profile_page(account_name,user,driver):
    """
    Once on the profile of a target account, this function tries to follow it.
    Returns 0 if there is an error, or if the account is already followed.
    """
    dataAPI().log(user,"follow_from_profile_page","INFO","start")
    follow_button_text = UIComponentsAPI().get_text("profile_page_follow_button",user,driver)
    if follow_button_text==0:
        dataAPI().log(user,"follow_from_profile_page","ERROR","couldn't access follow button")
        return 0
    elif follow_button_text!="Follow":
        dataAPI().log(user,"follow_from_profile_page","INFO","already following this dude, next")
        return 0
    else:
        return UIComponentsAPI().click("profile_page_follow_button",user,driver)

def get_account_data_from_profile_page(user,driver):
    dataAPI().log(user,"get_account_data_from_profile_page","INFO","start")
    username = UIComponentsAPI().get_text("profile_page_target_username",user,driver)
    name = UIComponentsAPI().get_text("profile_page_target_name",user,driver)
    nb_followers = UIComponentsAPI().get_text("profile_page_target_nb_followers",user,driver)
    nb_following = UIComponentsAPI().get_text("profile_page_target_nb_following",user,driver)
    nb_posts = UIComponentsAPI().get_text("profile_page_target_nb_posts",user,driver)    
    description = UIComponentsAPI().get_text("profile_page_target_description",user,driver)
    nb_likes_per_post = 0 ## incoming
    if description == 0:
        description = ""
    ### Everything is required except the description
    if 0 in  [username,name,nb_posts,nb_followers,nb_following]:
        dataAPI().log(user,"get_account_data_from_profile_page","ERROR","couldn't scrape raw account data properly. What we got : {0}, {1}, {2}, {3}, {4}".format(username,name,nb_followers,nb_following,nb_posts))
        return []
    ### Now, if we managed to extract the raw fields, we need to transform them
    try:
        nb_posts = treat_number(nb_posts,user)
        nb_followers = treat_number(nb_followers,user)
        nb_following = treat_number(nb_following,user)
    except:
        dataAPI().log(user,"get_account_data_from_profile_page","ERROR","couldn't properly transform raw account data properly.")
        return []
    dataAPI().log(user,"get_account_data_from_profile_page","INFO","raw account data scraped and transformed successfully : {0}, {1}, {2}, {3}, {4}".format(username,name,nb_followers,nb_following,nb_posts))
    return [username,name,nb_followers,nb_following,nb_posts,description,nb_likes_per_post]

    
############################################################################################################
################################## Random utilities functions #########################################
############################################################################################################

 
def generate_daily_poisson_times(start_day,stop_day,nb_actions_per_day):
    """Generates instants (datetimes) between start_day and stop_day following a Poisson law"""
    instant = start_day + datetime.timedelta(seconds = 20)
    moments = [instant]
    while instant < stop_day:
        n = random.random()
        inter_time_seconds = (-math.log(1.0 - n) / nb_actions_per_day)*(16*3600)
        inter_time_seconds = max(inter_time_seconds,3*60)
        instant = instant + datetime.timedelta(seconds = inter_time_seconds)
        moments+=[instant]
    return moments

def treat_number(s,user):
    s = s.split(" ")[0]
    s = s.replace(',',"")
    if 'K' in s or 'k' in s:
        s = s.replace('K',"")
        s = s.replace('k',"")
        s = float(s)
        s*=1000
        return int(s)
    if "m" in s or "M" in s:
        s = s.replace('m',"")
        s = s.replace('M',"")
        s = float(s)
        s*=1000000
        return int(s)
    return int(s)


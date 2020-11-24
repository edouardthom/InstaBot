#!/usr/bin/env python3

from instabot_data_api import dataAPI
from instabot_ui_api import UIComponentsAPI

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
import numpy as np
import datetime
import pandas as pd
import traceback
    

############################################################################################################
############################# The 5 Main independent blocks #############################################
############################################################################################################


def log_in(email,password,user,for_aws=True,headless=False):
    dataAPI().log(user,"log_in","INFO","start") 
    try:
        if for_aws:
            chrome_options = Options()
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            #chrome_options.add_argument('start-maximized')
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
            sleep(3)
            return driver
    except:
        dataAPI().log(user,"log_in","ERROR","failed, full exception : {}".format(traceback.format_exc()))  
        sleep(3)
        return 0


def update_followers_data(user,driver):
    dataAPI().log(user,"update_followers","INFO","start")
    try:
        profile_url = 'https://www.instagram.com/{}/'.format(user)
        if driver.current_url!=profile_url:
            driver.get(profile_url)
        sleep(2)
        
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
        sleep(3)
        return 1
    except:
        dataAPI().log(user,"update_followers","ERROR","UNIDENTIFIED failure, full exception : {}".format(traceback.format_exc())) 
        sleep(3)
        return 0
    


def unfollow_accounts(user,driver):
    try:
        dataAPI().log(user,"unfollow_accounts","INFO","start")
        
        ### Get the follows made by the bot
        follow_actions = dataAPI().get("follow_actions",user)
        
        ### Identify the accounts that the bot followed that need to be unfollowed because the time has come 
        # Reminder : In the function explore_hashtag, each account followed by the bot is assigned a number of hours before the unfollow must happen
        follow_actions['follow_time'] = follow_actions['follow_time'].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f"))
        follow_actions["planned_unfollow_date"] = follow_actions["follow_time"] + follow_actions.hours_before_unfollowing.apply(lambda x:datetime.timedelta(hours=x))
        accounts_to_unfollow = follow_actions[(follow_actions.planned_unfollow_date<=datetime.datetime.now())
                                             &(follow_actions.unfollow_time.isnull())]
        accounts_to_unfollow = accounts_to_unfollow.account_username
        
        ### Then we (try to) unfollow these accounts
        dataAPI().log(user,"unfollow_accounts","INFO","{} accounts to unfollow...".format(str(len(accounts_to_unfollow))))
        nb_of_accounts_unfollowed = 0
        sleep(1)
        for u in accounts_to_unfollow:
            sleep(1)
            unfollowing_success = unfollow_one_account(u,user,driver)
            nb_of_accounts_unfollowed+=unfollowing_success
        # remark : we can fail to unfollow an account because we were not following it. (the bot is not the only entity to have the ability to unfollow accounts)
        dataAPI().log(user,"unfollow_accounts","INFO","{} accounts successfully unfollowed".format(nb_of_accounts_unfollowed))
        return 1
    except:
        dataAPI().log(user,"unfollow_accounts","ERROR","UNIDENTIFIED failure, full exception : {}".format(traceback.format_exc())) 
        sleep(3)
        return 0           


def update_follow_actions_data(user,driver):
    try:
        ### Get the follows made by the bot
        follow_actions = dataAPI().get("follow_actions",user)
        
        ### We get the list of accounts followed by the user to update the follow data
        profile_url = 'https://www.instagram.com/{}/'.format(user)
        driver.get(profile_url)
        following = get_followers_following_for_user("following",user,driver)
    
        if type(following) ==int : 
            dataAPI().log(user,"update_follow_actions_data","ERROR","failed to get the following list -> stop the function execution")
            sleep(3)
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
        sleep(3)
        return 1
    except:
        dataAPI().log(user,"update_follow_actions_data","ERROR","UNIDENTIFIED failure, full exception : {}".format(traceback.format_exc())) 
        sleep(3)
        return 0        
 
    
def follow_accounts_from_hashtag(hashtag,nb_follows,user,driver):
    dataAPI().log(user,"explore_hashtag","INFO","start, #{}".format(hashtag))  
    
    driver.get('https://www.instagram.com/explore/tags/'+ hashtag + '/')
    sleep(2)
    ok = UIComponentsAPI().click("first_thumbnail_photo",user,driver)
    if ok==0:
        dataAPI().log(user,"explore_hashtag","ERROR","fail, full exception : {}".format(traceback.format_exc()))  
        sleep(3)
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
        if failures>=4:
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
        account_username,nb_posts,nb_followers,nb_following = get_account_data_from_profile_page(user,driver)   
        if None in [account_username,nb_posts,nb_followers,nb_following]:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            right_arrow_pressed = press_righ_arrow(pic_number,user,driver)
            if right_arrow_pressed == 0:
                dataAPI().log(user,"explore_hashtag","ERROR","stop the processing of hashtag {}".format(hashtag))
                break
            failures+=1
            continue
        
        ### Step 3
        follow_success = follow_from_profile_page(user,driver)  
        if follow_success==0:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            right_arrow_pressed = press_righ_arrow(pic_number,user,driver)
            if right_arrow_pressed == 0:
                dataAPI().log(user,"explore_hashtag","ERROR","stop the processing of hashtag {}".format(hashtag))
                break
            pic_number+=1
            failures+=1
            continue
        dataAPI().log(user,"explore_hashtag","INFO","successfully followed account : {}".format(account_username))

        ### The 3 steps succeeded, lets' move to the less inportrant bits 
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
         
        first_pic_liked = 0
        if np.random.randint(2):
            first_pic_liked = UIComponentsAPI().click("pictures_carousel_like_button",user,driver)
        
        ### IMPORTANT VARIABLE : number of hours max before unfollowing !
        ### The bot follows each accounts for a random limited amount of hours - between 2 and 24 hours.
        hours_before_unfollowing =  np.random.randint(2,24,1)[0]
         
                          
        record = {"follow_time" : datetime.datetime.now(),
                  "account_username" : account_username,
                  "account_nb_followers" : nb_followers,
                  "account_nb_following" : nb_following,
                  "account_nb_posts" : nb_posts,
                  "hashtag" : hashtag, 
                  "first_pic_liked" : first_pic_liked,
                  "hours_before_unfollowing" : hours_before_unfollowing,
                  "unfollow_time" : None}
        dataAPI().add_record("follow_actions",user,record)
        nb_accounts_followed+=1
        
        success_right_arrow_press = press_righ_arrow(pic_number,user,driver)
        if success_right_arrow_press==0:
            dataAPI().log(user,"explore_hashtag","ERROR","stop the processing of hashtag {}".format(hashtag))
            break
        pic_number=1
        
    
    dataAPI().log(user,"explore_hashtag","INFO","hashtag {0} processed, {1} accounts followed".format(hashtag,nb_accounts_followed))
    sleep(3)
    return 1
        

############################################################################################################
#################################### Secondary handy functions #############################################
############################################################################################################



def get_followers_following_for_user(entry,user,driver):
    nb_max_attempts = 3
    attempt = 1
    dataAPI().log(user,"get_followers_following_for_user","INFO","start - first attempt to get the {} data".format(entry))
    while attempt <= nb_max_attempts:
        sleep(2)
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
    except:
        dataAPI().log(user,"get_followers_following_for_user_one_try","ERROR","couldn't load user profile page")
        return (0,0)
    sleep(1)
    ### Open the followers/ing scrollable window from the profile page + get the # of entries
    if entry == "followers":
        nb_entries = UIComponentsAPI().get_text_and_click("profile_page_followers_button",user,driver)
    else:
        nb_entries = UIComponentsAPI().get_text_and_click("profile_page_following_button",user,driver)
    if nb_entries==0:
        return (0,0)
    sleep(1)
    try:
        nb_entries = treat_number(nb_entries,user)
        #find all elements in list
        fBody_xpath = "//div[@class='isgrP']"    
        fBody = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, fBody_xpath)))
        
        scroll = 0
        while scroll < nb_entries: # each scroll displays ~12 row, we divide by 3 to be reaaaallllyyy sure we don't miss any
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
            sleep(1)
            scroll += 1
        
        entries = []
        fails = 0
        sleep(2)
        for n in range(1,nb_entries):
            if fails>3:
                dataAPI().log(user,"get_followers_following_for_user_one_try","ERROR","too many fails to get the entries, stopping execution")
                return (0,0)
            try:
                xpath = "/html/body/div[5]/div/div/div[2]/ul/div/li[{}]".format(n)
                info = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,xpath))).text
                name = info.split("\n")[0]
                entries.append(name)
            except:
                fails+=1
                dataAPI().log(user,"get_followers_following_for_user_one_try","ERROR","couldn't get entry {}".format(n))
                pass

        dataAPI().log(user,"get_followers_following_for_user_one_try","INFO","{} entries scraped : {}/{}".format(entry,len(entries),nb_entries))
        return (entries,nb_entries)
    
    except:
        dataAPI().log(user,"get_followers_following_for_user_one_try","ERROR","UNIDENTIFIED failure, full exception : {}".format(traceback.format_exc())) 
        return (0,0)






def unfollow_one_account(user_to_unfollow,user,driver):
    """
    Parameters
    ----------
    user_to_unfollow : str
        The name of the account the bot will unfollow.
    user : TYPE
        the user tyhe bot is working for
    driver : TYPE
        The current selenium webdriver.

    Returns
    -------
    int
        1 if the account was succesfully followed, ie if the "unfollow" button was pressed.
        0 if something failed and the account couldn't be unfollowed (several possible reasons).
    """
    dataAPI().log(user,"unfollow_account_from_profile_page","INFO","start, user_to_unfollow={}".format(user_to_unfollow))
    try:
        driver.get('https://www.instagram.com/{}/'.format(user_to_unfollow))
    except:
        dataAPI().log(user,"unfollow_account_from_profile_page","ERROR","failed to access profile URL")
        return 0
    sleep(1)
    ok = UIComponentsAPI().click("unfollow_button",user,driver)
    if ok==0:
        dataAPI().log(user,"unfollow_account_from_profile_page","ERROR","Failed to unfollow user {} - 1st unfollow click".format(user_to_unfollow))
        return 0
    sleep(2)
    ok = UIComponentsAPI().click("unfollow_red_button_confirm",user,driver)
    if ok==1:
        dataAPI().log(user,"unfollow_account_from_profile_page","INFO","success, account {} unfollowed".format(user_to_unfollow))
        return 1
    else:
        dataAPI().log(user,"unfollow_account_from_profile_page","ERROR","Failed to unfollow user {} - 2nd unfollow click".format(user_to_unfollow))
        return 0


    

    
def press_righ_arrow(pic_number,user,driver):
    if pic_number==0:
        return UIComponentsAPI().click("pictures_carousel_first_pic_right_arrow",user,driver)
    else:
        return UIComponentsAPI().click("pictures_carousel_not_first_pic_right_arrow",user,driver)

    

def follow_from_profile_page(user,driver):
    """
    Once on the profile of a target account, this function tries to follow it.
    Returns 0 if there is an error, or if the account is already followed.
    """
    dataAPI().log(user,"follow_from_profile_page","INFO","start")
    follow_button_text = UIComponentsAPI().get_text("profile_page_follow_button",user,driver)
    if follow_button_text==0:
        return 0
    elif follow_button_text!="Follow":
        dataAPI().log(user,"follow_from_profile_page","INFO","already following this dude, next")
        return 0
    else:
        return UIComponentsAPI().click("profile_page_follow_button",user,driver)



def get_account_data_from_profile_page(user,driver):
    dataAPI().log(user,"get_account_data_from_profile_page","INFO","start")
    nb_followers = UIComponentsAPI().get_text("profile_page_target_nb_followers",user,driver)
    nb_following = UIComponentsAPI().get_text("profile_page_target_nb_following",user,driver)
    nb_posts = UIComponentsAPI().get_text("profile_page_target_nb_posts",user,driver)    
    account_username = UIComponentsAPI().get_text("profile_page_target_username",user,driver)
    if 0 in  [account_username,nb_posts,nb_followers,nb_following]:
        dataAPI().log(user,"get_account_data_from_profile_page","ERROR","couldn't scrape raw account data properly. What we got : {0}, {1}, {2}, {3}".format(account_username,nb_followers,nb_following,nb_posts))
        return None,None,None,None
    ### Now, if we managed to extract the raw fields, we need to transform them
    try:
        nb_posts = treat_number(nb_posts,user)
        nb_followers = treat_number(nb_followers,user)
        nb_following = treat_number(nb_following,user)
    except:
        dataAPI().log(user,"get_account_data_from_profile_page","ERROR","couldn't properly transform raw account data properly.")
        return None,None,None,None
    dataAPI().log(user,"get_account_data_from_profile_page","INFO","raw account data scraped and transformed successfully : {0}, {1}, {2}, {3}".format(account_username,nb_followers,nb_following,nb_posts))
    return account_username,nb_posts,nb_followers,nb_following

    
    

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


  
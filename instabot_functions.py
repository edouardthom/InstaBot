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
    


def log_in(username,password,for_aws=True):
    print("Starting the log-in for {}...".format(username))
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
            driver = webdriver.Chrome()
        print("INFO : driver launched")
        
        driver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        print("INFO : authentication page loaded")
        
        UIComponentsAPI().click("login_accept_cookies",driver)
        UIComponentsAPI().enter_text("login_email_input_field",username,driver)
        UIComponentsAPI().enter_text("login_password_input_field",password,driver) 
        UIComponentsAPI().click("login_connexion_button",driver)
                
        print("Login successful for username {}.".format(username))
        return driver
    except:
        print("ABORTED : error while logging in")
        traceback.print_exc()
        return 0



def unfollow_account_from_profile_page(user_to_unfollow,driver):
    ok = UIComponentsAPI().click("unfollow_button",driver)
    if ok==0:
        print("Failed to unfollow user {}".format(user_to_unfollow))
        return 0
    sleep(2)
    ok = UIComponentsAPI().click("unfollow_red_button_confirm",driver)
    if ok==1:
        print("Account {} unfollowed".format(user_to_unfollow))
        return 1
    else:
        print("Failed to unfollow user {}".format(user_to_unfollow))
        return 0



def unfollowing_of_bot_followed_users(user,driver):
    
    follow_actions = dataAPI().get("follow_actions",user)
    
    print("Starting the unfollowing process...")
    follow_actions['follow_time'] = follow_actions['follow_time'].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f"))
    follow_actions["planned_unfollow_date"] = follow_actions["follow_time"] + follow_actions.days_before_unfollowing.apply(lambda x:datetime.timedelta(days=x))
    accounts_to_unfollow = follow_actions[(follow_actions.planned_unfollow_date<=datetime.datetime.now())
                                         &(follow_actions.unfollow_time.isnull())]
    accounts_to_unfollow = accounts_to_unfollow.account_username
    print("{} accounts to unfollow...".format(str(len(accounts_to_unfollow))))
    for u in accounts_to_unfollow:
        driver.get('https://www.instagram.com/{}/'.format(u))
        sleep(1)
        unfollow_account_from_profile_page(u,driver)
    print("Accounts were hopefully successfully unfollowed")
    
    ### Updating the follow dataframe about unfollow times of some accounts
    print("Now updating the unfollow data for user {}...".format(user))
    profile_url = 'https://www.instagram.com/{}/'.format(user)
    driver.get(profile_url)
    following = get_all_following_from_profile_page(user,driver)
    print("Following data OK")

    if type(following) ==int : #ie the function failed and returned 0
        print("ERROR : failed to get the followers list")
        return 0
        
    following = pd.DataFrame({"account_username":following,"following":1})
    follow_actions = follow_actions.merge(following,on="account_username",how="left")
    nb_new_unfollowings = ((follow_actions.following.isnull())&
                           (follow_actions["unfollow_time"].isnull())).sum()
    print('{0} new unfollowing since last update for user {1}'.format(nb_new_unfollowings,user))
    (follow_actions["unfollow_time"])[(follow_actions.following.isnull())
                                  &(follow_actions["unfollow_time"].isnull())] = datetime.datetime.now()
    follow_actions = follow_actions.drop("following",1)
    follow_actions = follow_actions.drop("planned_unfollow_date",1)
    dataAPI().store("follow_actions",user,follow_actions)
    print("Unfollow data for user {} successfully updated".format(user))

 

def update_followers(user,driver):
    print("Starting the update of the followers data for user {}...".format(user))
    try:
        profile_url = 'https://www.instagram.com/{}/'.format(user)
        if driver.current_url!=profile_url:
            driver.get(profile_url)

        sleep(2)
        
        followers_now = get_all_followers_from_profile_page(user,driver)

        if type(followers_now) == int :
            print("ERROR : failed to get the followers list")
            return 0
        
        followers_now = pd.DataFrame({"present_now":[1]*len(followers_now),
                                      "account_username":followers_now})
        nb_followers = len(followers_now)
        print("Current list of followers obtained - currently {} followers".format(str(nb_followers)))
        
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
        
        print("Followers data successfully updated for user {} !".format(user))
        return 1
    except:
        print("ERROR : couldn't update the list of followers")
        traceback.print_exc()
        return 0





    
    
def get_all_followers_from_profile_page(user,driver):
    print('From profile page, scraping of the list of followers...')
    ### Open the followers scrollable window from the profile page
    nb_followers = UIComponentsAPI().get_text_and_click("profile_page_followers_button",driver)
    if nb_followers==0:
        return 0
    
    try:
        nb_followers = treat_number(nb_followers)
        #find all elements in list
        fBody_xpath = "//div[@class='isgrP']"    
        fBody = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, fBody_xpath)))
        
        scroll = 0
        while scroll < 10000:
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
            fList_xpath = "//div[@class='isgrP']//li"
            fList = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, fList_xpath)))
            sleep(0.5)
            if len(fList)>=nb_followers:
                break
            scroll += 1
        
        followers = pd.Series(fList).apply(lambda x:x.text.split("\n")[0])
        
        return followers
    
    except:
        print("ERROR : get_all_followers_from_profile_page failure")
        traceback.print_exc()
        return 0



def get_all_following_from_profile_page(user,driver):
    print('From profile page, scraping of the list of following accounts...')
    ### Open the followers scrollable window from the profile page
    nb_following = UIComponentsAPI().get_text_and_click("profile_page_following_button",driver)
    if nb_following==0:
        return 0
    
    try:
        nb_following = treat_number(nb_following)
        
        #find all elements in list
        fBody_xpath = "//div[@class='isgrP']"    
        fBody = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, fBody_xpath)))
        
        scroll = 0
        while scroll < 10000: 
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
            fList_xpath = "//div[@class='isgrP']//li"
            fList = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, fList_xpath)))
            sleep(0.5)
            if len(fList)>=nb_following:
                break
            scroll += 1
        
        ### Sometimes the last element provokes an error :(
        # suspicion : depend son the # of followers : for ex 397 fail, 396 ok
        try:
            fList[-1].text
        except:
            fList = fList[:-1]
        ###########################
        
        following = pd.Series(fList).apply(lambda x:x.text.split("\n")[0])
        
        return following
    except:
        print("ERROR : get_all_following_from_profile_page failure")
        traceback.print_exc()
        return 0






def explore_hashtag(hashtag,nb_follows,user,driver):
    
    print("Starting exploring #{}...".format(hashtag))
    
    driver.get('https://www.instagram.com/explore/tags/'+ hashtag + '/')
    sleep(2)
    ok = UIComponentsAPI().click("first_thumbnail_photo",driver)
    if ok==0:
        print("ERROR : explore_hashtag failure")
        return 0
    sleep(1)
        
    pic_number = 0
    nb_accounts_followed = 0
    while nb_accounts_followed < nb_follows:
        
        account_username = UIComponentsAPI().get_text("picture_carousel_account_name",driver)
        if account_username==0:
            print("ERROR : stop the processing of hashtag {}".format(hashtag))
            break
        
        account_url = "https://www.instagram.com/"+account_username+"/"
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(account_url)        
        account_username,nb_posts,nb_followers,nb_followed = get_account_data_from_profile_page(driver)   

        if None in [account_username,nb_posts,nb_followers,nb_followed]:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            right_arrow_pressed = press_righ_arrow(pic_number,driver)
            if right_arrow_pressed == 0:
                print("ERROR : stop the processing of hashtag {}".format(hashtag))
                break
            continue
        
        follow_success = follow_from_profile_page(driver)  
        if follow_success==0:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            right_arrow_pressed = press_righ_arrow(pic_number,driver)
            if right_arrow_pressed == 0:
                print("ERROR : stop the processing of hashtag {}".format(hashtag))
                break
            pic_number+=1
            continue
        print("Account {} followed successfully !".format(account_username))

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
         
        first_pic_liked = 0
        if np.random.randint(2):
            first_pic_liked = UIComponentsAPI().click("pictures_carousel_like_button",driver)
                                           
        record = {"follow_time" : datetime.datetime.now(),
                  "account_username" : account_username,
                  "account_nb_followers" : nb_followers,
                  "account_nb_posts" : nb_posts,
                  "hashtag" : hashtag, 
                  "first_pic_liked" : first_pic_liked,
                  "days_before_unfollowing" : np.random.randint(1,5,1)[0],
                  "unfollow_time" : None}
        dataAPI().add_record("follow_actions",user,record)
               
        success_right_arrow_press = press_righ_arrow(pic_number,driver)
        if success_right_arrow_press==0:
            print("ERROR : stop the processing of hashtag {}".format(hashtag))
            break
        pic_number=1
        nb_accounts_followed+=1
    
    print("User {0} followed {1} accounts with hashtag {2}".format(user,nb_follows,hashtag))
    print("Hashtag {} done".format(hashtag))
    return 1
        
    

    
def press_righ_arrow(pic_number,driver):
    if pic_number==0:
        return UIComponentsAPI().click("pictures_carousel_first_pic_right_arrow",driver)
    else:
        return UIComponentsAPI().click("pictures_carousel_not_first_pic_right_arrow",driver)

    

def follow_from_profile_page(driver):
    follow_button_text = UIComponentsAPI().get_text("profile_page_follow_button",driver)
    if follow_button_text==0:
        return 0
    elif follow_button_text!="Follow":
        print("already following this dude, next")
        return 0
    else:
        return UIComponentsAPI().click("profile_page_follow_button",driver)



def get_account_data_from_profile_page(driver):
       
    nb_followers = UIComponentsAPI().get_text("profile_page_target_nb_followers",driver)
    nb_following = UIComponentsAPI().get_text("profile_page_target_nb_following",driver)
    nb_posts = UIComponentsAPI().get_text("profile_page_target_nb_posts",driver)    
    username = UIComponentsAPI().get_text("profile_page_target_username",driver)
    if 0 in  [username,nb_posts,nb_followers,nb_following]:
        print("ERROR while getting account data")
        return None,None,None,None
    else:
        return username,treat_number(nb_posts),treat_number(nb_followers),treat_number(nb_following)

    
    



def treat_number(s):
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



    
    
    

    
    









    
    
    
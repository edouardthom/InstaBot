#!/usr/bin/env python3

from selenium import webdriver
from time import sleep
import numpy as np
import datetime
import pandas as pd
import traceback
    

def unfollow_account_from_profile_page(user_to_unfollow,driver):
    try:
        following_xpath = '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button'
        following_button = driver.find_element_by_xpath(following_xpath)
        if following_button.text=="Following":
            following_button.click()
            sleep(1)
            unfollow_xpath = '/html/body/div[4]/div/div/div[3]/button[1]'
            driver.find_element_by_xpath(unfollow_xpath).click()
            print("Account {} unfollowed".format(user_to_unfollow))
        else:
            print("This user is currently not being followed")
        return 1
    except:
        print("ERROR : failed to unfollow the account")
        return 0


def unfollowing_of_bot_followed_users(user,driver):
    try:
        bot_follows = pd.read_csv("instaedobot_follow_actions_{}.csv".format(user))
    except:
        ### If the file is not there, the bot never followed anyone for that user
        return 0
    bot_follows['follow_time_by_user'] = bot_follows['follow_time_by_user'].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f"))
    bot_follows["planned_unfollow_date"] = bot_follows["follow_time_by_user"] + bot_follows.days_before_unfollowing.apply(lambda x:datetime.timedelta(days=x))
    accounts_to_unfollow = bot_follows[(bot_follows.planned_unfollow_date<=datetime.datetime.now())
                                       &(bot_follows.unfollowed==0)]
    accounts_to_unfollow = accounts_to_unfollow.target_username
    for u in accounts_to_unfollow:
        driver.get('https://www.instagram.com/{}/'.format(u))
        sleep(1)
        unfollow_account_from_profile_page(u,driver)
        (bot_follows[bot_follows.target_username==u])["unfollowed"] = 1


def temporize(user):
    while 1:
        try:
            follows = pd.read_csv("instaedobot_follow_actions_{}.csv".format(user))
        except:
            return 1
        now = datetime.datetime.now()
        one_hour_ago = now-datetime.timedelta(3600)
        one_day_ago = now-datetime.timedelta(24*3600)
        follows['follow_time_by_user'] = follows['follow_time_by_user'].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f"))
        nb_follows_past_hour = follows[follows.follow_time_by_user >= one_hour_ago].shape[0]
        nb_follows_past_day = follows[follows.follow_time_by_user >= one_day_ago].shape[0]
        has_to_wait = nb_follows_past_hour>20 or nb_follows_past_day>200
        if has_to_wait:
            print("Temporizing 3 minute... (to avoid reaching instagram limit and get flagged)")
            sleep(300)
        else:
            return 1

 

def update_followers(user,driver):
    try:
        profile_url = 'https://www.instagram.com/{}/'.format(user)
        if driver.current_url!=profile_url:
            driver.get(profile_url)
        try:
            data = pd.read_csv("followers_{}.csv".format(user))
        except:
            data = pd.DataFrame(columns = ["user",
                                           "follow_time_by_target",
                                           "unfollow_time_by_target"])
        sleep(2)
        
        ### This part often fails if the page is too long to load, we have to try several times
        tries = 0
        success = 0
        while tries<=2:
            try:
                followers_now = get_all_followers_from_profile_page(user,driver)
                success=1
                break
            except:
                traceback.print_exc()
                sleep(5)
                driver.get(profile_url)
                sleep(5)
                tries+=1
        if success ==0 :
            print("ERROR : failed to get the followers list")
            return 0
        followers_now = pd.DataFrame({"present_now":[1]*len(followers_now),
                                      "user":followers_now})
        data = data.merge(followers_now,how="outer",on="user")
        
        data["unfollow_time_by_target"][(data.present_now.isnull())
                              &(data.unfollow_time_by_target.isnull())] = datetime.datetime.now()
        data["unfollow_time_by_target"][(data.present_now==1)
                              &(~data.unfollow_time_by_target.isnull())] = None
                
        data = data.fillna({"follow_time_by_target":datetime.datetime.now()})
        data = data.drop("present_now",1)
        data.to_csv("followers_{}.csv".format(user),index=False)
        return 1
    except:
        print("ERROR : couldn't update the list of followers")
        traceback.print_exc()
        return 0




def get_all_followers_from_profile_page(user,driver):
    ### Open the followers scrollable window from the profile page
    followers_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span'
    followers_button = driver.find_element_by_xpath(followers_xpath)
    nb_followers = followers_button.text
    nb_followers = treat_number(nb_followers)
    
    followers_button.click()
    
    sleep(2)
    #find all elements in list
    fBody  = driver.find_element_by_xpath("//div[@class='isgrP']")
    scroll = 0
    while scroll < 10000: # scroll 5 times
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
        fList  = driver.find_elements_by_xpath("//div[@class='isgrP']//li")    
        sleep(0.5)
        if len(fList)>=nb_followers:
            break
        scroll += 1
    
    followers = pd.Series(fList).apply(lambda x:x.text.split("\n")[0])
    
    return followers




def get_all_following_from_profile_page(user,driver):
    following_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span'
    following_button = driver.find_element_by_xpath(following_xpath)
    nb_following = following_button.text
    nb_following = treat_number(nb_following)
    
    following_button.click()
    
    #find all elements in list
    fBody  = driver.find_element_by_xpath("//div[@class='isgrP']")
    scroll = 0
    while scroll < 10000: # scroll 5 times
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
        fList  = driver.find_elements_by_xpath("//div[@class='isgrP']//li")    
        sleep(0.5)
        if len(fList)>=nb_following:
            break
        scroll += 1
    
    following = pd.Series(fList).apply(lambda x:x.text.split("\n")[0])
    
    return following








def log_in(username,password):
    try:
        driver = webdriver.Chrome()  
        
        driver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        
        sleep_random_time(2,3)
        
        username_field = driver.find_element_by_name('username')
        username_field.send_keys(username)
        password_field = driver.find_element_by_name('password')
        password_field.send_keys(password)
        
        sleep_random_time(0.5,1)
        
        connexion_button = '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button/div'
        driver.find_element_by_xpath(connexion_button).click()
        
        sleep_random_time(1,1.5)
        

        print("Login successful")
        return driver
    except:
        print("ABORTED : error while logging in")
        traceback.print_exc()
        return 0



def explore_hashtag(hashtag,nb_follows,user,driver):
    
    print("Exploring #{}".format(hashtag))
    
    try:
        driver.get('https://www.instagram.com/explore/tags/'+ hashtag + '/')
        sleep_random_time(0.5,1)
        first_thumbnail_photo = '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div'
        driver.find_element_by_xpath(first_thumbnail_photo).click()
    except:
        print("ERROR : cannot reach pics of this hashtag")
        traceback.print_exc()
    
    sleep_random_time(0.5,1.5)
    
    ### click on the 1st thumbnail photo
    # remark : in the following xpath, the div[X]/div[Y] refers to the thumbnail photo
    # row X column Y. But no need to get more than the first one, it's easier to open 
    # the 1st one and then use the arrows to move to the next ones
        
    sleep_random_time(0.5,1)
    pic_number = 0
    n = 0
    while n<nb_follows:
            
        ### To avoid being blocked by instagram we temporize
        temporize(user)
            
        ### Get the account name
        try:
            account_name_button = '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a'
            username = driver.find_element_by_xpath(account_name_button).text
        except:
            print("ERROR : coundn't access the account name")
            press_righ_arrow(pic_number,driver)
            pic_number=1
            continue
        
        account_url = "https://www.instagram.com/"+username+"/"
        
        # Open a new window
        driver.execute_script("window.open('');")
        # Switch to the new window and open URL B
        driver.switch_to.window(driver.window_handles[1])
        driver.get(account_url)
        
        ### Get the data
        username,nb_posts,nb_followers,nb_followed = get_account_data_from_profile_page(driver)

        sleep_random_time(1,1.5)
        
        ### Follow the guy
        follow_success = try_to_follow_from_profile_page(driver)  
        sleep_random_time(1,2)
        
        # Close the tab with URL B
        driver.close()
        # Switch back to the first tab with URL A
        driver.switch_to.window(driver.window_handles[0])
        
        sleep_random_time(1,1.5)
        
        if follow_success==0 or username==None:
            press_righ_arrow(pic_number,driver)
            pic_number=1
            continue
        
        ### Possibly like the 1st pic
        first_pic_liked = 0
        if random_yes_or_no():
            first_pic_liked = like_1st_pic(driver)
        sleep_random_time(1,1.5)
            
        ### Number of days before unfollowing
        days_before_unfollowing = np.random.randint(1,8,1)[0]
        
        ### Now we update the follow data
        data_to_append = pd.DataFrame({"hashtag":[hashtag],
                                        "follow_time_by_user":[datetime.datetime.now()],
                                        "first_pic_liked":[first_pic_liked],
                                         "target_username":[username],
                                         "target_nb_followers":[nb_followers],
                                         "target_nb_followed":[nb_followed],
                                         "target_nb_posts":[nb_posts],
                                         "days_before_unfollowing":[days_before_unfollowing],
                                         "unfollowed":[0]})
        try:
            data = pd.read_csv("instaedobot_follow_actions_{}.csv".format(user))
        except:
            columns_instaedobot_follow_actions = ["hashtag",
                                      "first_pic_liked",
                                      "target_username",
                                      "target_nb_followers",
                                      "target_nb_followed",
                                      "target_nb_posts",
                                      "follow_time_by_user",
                                      "days_before_unfollowing",
                                      "unfollowed"]
            data = pd.DataFrame(columns = columns_instaedobot_follow_actions)
            
        data = data.append(data_to_append,ignore_index=True,sort=True)
        data.to_csv("instaedobot_follow_actions_{}.csv".format(user),index=False)
        print("User processed with success !")
        
        
        ### Go to the next thumbnail pic for our hashtag
        # the right arrow will be pressed 1 or 2 times at random        
        press_righ_arrow(pic_number,driver)
        pic_number=1

        n+=1
        
        sleep(5)
    
    print("Hashtag {} done".format(hashtag))
    return 1
        
    
    
def press_righ_arrow(pic_number,driver):
    nb_press_arrow = np.random.randint(1,3)
    
    if pic_number==0:
        arrow_right = '/html/body/div[4]/div[1]/div/div/a'
        driver.find_element_by_xpath(arrow_right).click()
        sleep_random_time(1,1.5)            
        
    else:
        for _ in range(nb_press_arrow):
            arrow_right = '/html/body/div[4]/div[1]/div/div/a[2]'
            driver.find_element_by_xpath(arrow_right).click()
            sleep_random_time(1.5,2)
    return 1

    

def try_to_follow_from_profile_page(driver):
    try:
        follow_button_xpath = '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button'
        follow_button = driver.find_element_by_xpath(follow_button_xpath)
        text = follow_button.text
        if text == "Follow":
            follow_button.click()
            return 1
        elif text == "Following":
            print("already following this dude, next")
            return 0
        else:
            return 0
    except:
        print("ERROR trying to follow")
        traceback.print_exc() 
        return 0


def get_account_data_from_profile_page(driver):
    
   
    try:
        nb_followers_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span'
        nb_followers = driver.find_element_by_xpath(nb_followers_xpath).text
        nb_followers = treat_number(nb_followers)
        
        nb_followed_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a'
        nb_followed = driver.find_element_by_xpath(nb_followed_xpath).text
        nb_followed = treat_number(nb_followed)
        
        nb_posts_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[1]/span/span'
        nb_posts = driver.find_element_by_xpath(nb_posts_xpath).text
        nb_posts = treat_number(nb_posts)
        
        username_xpath = '//*[@id="react-root"]/section/main/div/header/section/div[1]/h1'
        username = driver.find_element_by_xpath(username_xpath).text
        
        return username,nb_posts,nb_followers,nb_followed
    except:
        print("ERROR while getting account data")
        traceback.print_exc()  
        return None,None,None,None
    
    


def like_1st_pic(driver):
    try :
        like_button_xpath = '/html/body/div[4]/div[2]/div/article/div[2]/section[1]/span[1]/button/span'
        driver.find_element_by_xpath(like_button_xpath).click()
        return 1
    except:
        print("ERROR trying to like the 1st pic")
        return 0
        


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



def random_yes_or_no():
    return bool(np.random.randint(2))


def sleep_random_time(mini=1,maxi=2):
    sleep_time = np.random.uniform(mini,maxi,1)[0]
    sleep(sleep_time)
    
    
    

    
    
    









    
    
    
#!/usr/bin/env python3

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
    

def unfollow_account_from_profile_page(user_to_unfollow,driver):
    unfollowing_xpath = '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button'
    unfollowing_button = get_and_click_element(unfollowing_xpath,driver,click=False)
    if unfollowing_button==0:
        print("ERROR : unfollow_account_from_profile_page failure (user : {})".format(user_to_unfollow))
        return 0  
    elif unfollowing_button.text=="Following":
        try:
            unfollowing_button.click()
            unfollow_confirmation_xpath = "/html/body/div[4]/div/div/div[3]/button[1]"
            unfollowed = get_and_click_element(unfollow_confirmation_xpath,driver,click=True)
            if unfollowed!=0:
                print("Account {} unfollowed".format(user_to_unfollow))
                return 1
            else:
                print("Failed to unfollow user {}".format(user_to_unfollow))
        except:
            print("Failed to unfollow user {}".format(user_to_unfollow))
        
    else:
        print("This user is currently not being followed")
        return 1


def unfollowing_of_bot_followed_users(user,driver):
    
    try:
        bot_follows = pd.read_csv("instaedobot_follow_actions_{}.csv".format(user))
    except:
        ### If the file is not there, the bot never followed anyone for that user
        return 0
    print("Starting the unfollowing process...")
    bot_follows['follow_time_by_user'] = bot_follows['follow_time_by_user'].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f"))
    bot_follows["planned_unfollow_date"] = bot_follows["follow_time_by_user"] + bot_follows.days_before_unfollowing.apply(lambda x:datetime.timedelta(days=x))
    accounts_to_unfollow = bot_follows[(bot_follows.planned_unfollow_date<=datetime.datetime.now())
                                       &(bot_follows.unfollow_time_by_user.isnull())]
    accounts_to_unfollow = accounts_to_unfollow.target_username
    print("{} accounts to unfollow...".format(str(len(accounts_to_unfollow))))
    for u in accounts_to_unfollow:
        driver.get('https://www.instagram.com/{}/'.format(u))
        sleep(1)
        unfollow_account_from_profile_page(u,driver)
    print("{} accounts were successfully treated".format(len(accounts_to_unfollow)))
    
    ### Updating the follow dataframe about unfollow times of some accounts
    print("Now updating the unfollow data for user {}...".format(user))
    print("Reminder : some unfollow are made by the bot, but we also want to log the unfollows made by the user himself.")
    profile_url = 'https://www.instagram.com/{}/'.format(user)
    driver.get(profile_url)
    following = get_all_following_from_profile_page(user,driver)
    print("Following data OK")

    if type(following) ==int : #ie the function failed and returned 0
        print("ERROR : failed to get the followers list")
        return 0
        
    following = pd.DataFrame({"target_username":following,"following":1})
    bot_follows = bot_follows.merge(following,on="target_username",how="left")
    nb_new_unfollowings = ((bot_follows.following.isnull())&(bot_follows["unfollow_time_by_user"].isnull())).sum()
    print('{0} new unfollowing since last update for user {1}'.format(nb_new_unfollowings,user))
    (bot_follows["unfollow_time_by_user"])[(bot_follows.following.isnull())
                                  &(bot_follows["unfollow_time_by_user"].isnull())] = datetime.datetime.now()
    bot_follows = bot_follows.drop("following",1)
    bot_follows = bot_follows.drop("planned_unfollow_date",1)
    bot_follows.to_csv("instaedobot_follow_actions_{}.csv".format(user),index=False)
    print("Unfollow data for user {} successfully updated".format(user))

 

def update_followers(user,driver):
    print("Starting the update of the followers data for user {}...".format(user))
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
        followers_now = get_all_followers_from_profile_page(user,driver)

        if type(followers_now) == int :
            print("ERROR : failed to get the followers list")
            return 0
        
        followers_now = pd.DataFrame({"present_now":[1]*len(followers_now),
                                      "user":followers_now})
        nb_followers = len(followers_now)
        print("Current list of followers obtained - currently {} followers".format(str(nb_followers)))
        data = data.merge(followers_now,how="outer",on="user")
        
        data["unfollow_time_by_target"][(data.present_now.isnull())
                              &(data.unfollow_time_by_target.isnull())] = datetime.datetime.now()
        data["unfollow_time_by_target"][(data.present_now==1)
                              &(~data.unfollow_time_by_target.isnull())] = None
                
        data = data.fillna({"follow_time_by_target":datetime.datetime.now()})
        data = data.drop("present_now",1)
        data.to_csv("followers_{}.csv".format(user),index=False)
        print("Followers data successfully updated for user {} !".format(user))
        return 1
    except:
        print("ERROR : couldn't update the list of followers")
        traceback.print_exc()
        return 0





    
    
def get_all_followers_from_profile_page(user,driver):
    print('From profile page, scraping of the list of followers...')
    ### Open the followers scrollable window from the profile page
    followers_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span'
    followers_button = get_and_click_element(followers_xpath,driver)
    if followers_button==0:
        print("ERROR : get_all_followers_from_profile_page failure")
        return 0
    
    try:
        nb_followers = followers_button.text
        nb_followers = treat_number(nb_followers)
        
        sleep(1)
        #find all elements in list
        fBody_xpath = "//div[@class='isgrP']"    
        fBody = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, fBody_xpath)))
        
        scroll = 0
        while scroll < 10000: # scroll 5 times
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
            fList_xpath = "//div[@class='isgrP']//li"
            fList = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, fList_xpath)))
            sleep(0.5)
            if len(fList)>=nb_followers:
                break
            scroll += 1
        
        followers = pd.Series(fList).apply(lambda x:x.text.split("\n")[0])
        
        return followers
    
    except:
        print("ERROR : get_all_followers_from_profile_page failure")
        print("FYI Exception : \n")
        traceback.print_exc()
        print("\n")
        return 0



def get_all_following_from_profile_page(user,driver):
    print('From profile page, scraping of the list of "following" accounts...')
    ### Open the followers scrollable window from the profile page
    following_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span'
    following_button = get_and_click_element(following_xpath,driver)
    if following_button==0:
        print("ERROR : get_all_following_from_profile_page failure")
        return 0
    
    try:
        nb_following = following_button.text
        nb_following = treat_number(nb_following)
        
        sleep(1)
        #find all elements in list
        fBody_xpath = "//div[@class='isgrP']"    
        fBody = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, fBody_xpath)))
        
        scroll = 0
        while scroll < 10000: 
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
            fList_xpath = "//div[@class='isgrP']//li"
            fList = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, fList_xpath)))
            sleep(0.5)
            if len(fList)>=nb_following:
                break
            scroll += 1
        
        ### Sometimes the last element provokes an error :(
        # suspicion : depend son the # of followers : 397 fail, 396 ok
        try:
            fList[-1].text
        except:
            fList = fList[:-1]
        ###########################
        
        following = pd.Series(fList).apply(lambda x:x.text.split("\n")[0])
        
        return following
    except:
        print("ERROR : get_all_following_from_profile_page failure")
        print("FYI Exception : \n")
        traceback.print_exc()
        print("\n")
        return 0









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
        
        sleep_random_time(2,3)
        
        username_field = driver.find_element_by_name('username')
        username_field.send_keys(username)
        password_field = driver.find_element_by_name('password')
        password_field.send_keys(password)
        
        sleep_random_time(0.5,1)
        
        connexion_button = '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button/div'
        driver.find_element_by_xpath(connexion_button).click()
        
        sleep_random_time(1,1.5)
        

        print("Login successful for username {}.".format(username))
        return driver
    except:
        print("ABORTED : error while logging in")
        traceback.print_exc()
        return 0




def explore_hashtag(hashtag,nb_follows,user,driver):
    
    print("Starting exploring #{}...".format(hashtag))
    
    driver.get('https://www.instagram.com/explore/tags/'+ hashtag + '/')
    sleep(1)
    first_thumbnail_photo_xpath = '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div'
    ok = get_and_click_element(first_thumbnail_photo_xpath,driver)
    if ok==0:
        print("ERROR : explore_hashtag failure")
        traceback.print_exc()
        return 0
    
    sleep(1)
    
    ### click on the 1st thumbnail photo
    # remark : in the following xpath, the div[X]/div[Y] refers to the thumbnail photo
    # row X column Y. But no need to get more than the first one, it's easier to open 
    # the 1st one and then use the arrows to move to the next ones
        
    sleep_random_time(1.5,2)
    pic_number = 0
    n = 0
    while n<nb_follows:
        
        ### Get the account name
        username_ok=0
        account_name_possible_xpaths = ['html/body/div[4]/div[1]/div/div/a',
                                        '/html/body/div[3]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a',
                                        '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a']
        for xpath in account_name_possible_xpaths:
            try:
                # If it fails we don't reload, otherwise we'd loose the view with the arrows right/left
                account_name_button = get_and_click_element(xpath,driver,click=False,
                                                            two_tries_with_reload=False,print_exception=False)
                un = account_name_button.text
            except:
                un = 'Next'
            if un!="Next" and un!="Previous":
                username=un
                username_ok=1
                break
        if username_ok==0:
            print("ERROR : coundn't access the account name")
            success_right_arrow_press = press_righ_arrow(pic_number,driver)
            if success_right_arrow_press==0:
                print("ERROR : stop the processing of hashtag {}".format(hashtag))
                break
            pic_number=1   
            continue           
        
        account_url = "https://www.instagram.com/"+username+"/"
        
        # Open a new window
        driver.execute_script("window.open('');")
        # Switch to the new window and open URL B
        driver.switch_to.window(driver.window_handles[1])
        driver.get(account_url)
        sleep(2)
        
        ### Get the data
        username,nb_posts,nb_followers,nb_followed = get_account_data_from_profile_page(driver)        
        sleep(1)
        
        ### Follow the guy - only if we correctly got the data (for data quality)
        follow_success = 0
        if None not in [username,nb_posts,nb_followers,nb_followed]:
            follow_success = try_to_follow_from_profile_page(driver)  
            sleep(1)
        
        # Close the tab with URL B
        driver.close()
        # Switch back to the first tab with URL A
        driver.switch_to.window(driver.window_handles[0])
        sleep(1)
        
        ### If we failed to get the data, or to follow the guy, we move to the next one
        if follow_success==0:
            success_right_arrow_press = press_righ_arrow(pic_number,driver)
            if success_right_arrow_press==0:
                print("ERROR : stop the processing of hashtag {}".format(hashtag))
                break
            sleep(1)
            pic_number=1
            continue
        
        ### Possibly like the 1st pic
        first_pic_liked = 0
        if random_yes_or_no():
            first_pic_liked = like_1st_pic(driver)
            sleep(1)
            
        ### Number of days before unfollowing
        days_before_unfollowing = np.random.randint(1,4,1)[0]
        
        ### Now we update the follow data
        data_to_append = pd.DataFrame({"hashtag":[hashtag],
                                        "follow_time_by_user":[datetime.datetime.now()],
                                        "first_pic_liked":[first_pic_liked],
                                         "target_username":[username],
                                         "target_nb_followers":[nb_followers],
                                         "target_nb_followed":[nb_followed],
                                         "target_nb_posts":[nb_posts],
                                         "days_before_unfollowing":[days_before_unfollowing],
                                         "unfollow_time_by_user":[None]})
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
                                      "unfollow_time_by_user"]
            data = pd.DataFrame(columns = columns_instaedobot_follow_actions)
            
        data = data.append(data_to_append,ignore_index=True,sort=True)
        data.to_csv("instaedobot_follow_actions_{}.csv".format(user),index=False)
        print("User {} processed with success !".format(username))
        
        
        ### Go to the next thumbnail pic for our hashtag
        # the right arrow will be pressed 1 or 2 times at random        
        success_right_arrow_press = press_righ_arrow(pic_number,driver)
        if success_right_arrow_press==0:
            print("ERROR : stop the processing of hashtag {}".format(hashtag))
            break
        pic_number=1

        n+=1
        
        sleep(2)
    
    print("User {0} followed {1} accounts with hashtag {2}".format(user,nb_follows,hashtag))
    print("Hashtag {} done".format(hashtag))
    return 1
        
    

    
def press_righ_arrow(pic_number,driver):
    if pic_number==0:
        arrow_right_xpath = '/html/body/div[4]/div[1]/div/div/a'
        button = get_and_click_element(arrow_right_xpath,driver)
        ### If we fail to click the right arrow
        if button==0:
            traceback.print_exc() 
            print("ERROR : couldn't click right arrow")
            sleep(1)
            return 0
        sleep(1)  
    else:
        arrow_right_xpath = '/html/body/div[4]/div[1]/div/div/a[2]'
        button = get_and_click_element(arrow_right_xpath,driver)
        ### If we fail to click the right arrow
        if button==0:
            traceback.print_exc() 
            print("ERROR : couldn't click right arrow")
            sleep(1)
            return 0
        sleep(1)
    return 1

    

def try_to_follow_from_profile_page(driver):
    follow_button_xpath = '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button'
    follow_button = get_and_click_element(follow_button_xpath,driver,click=False)
    if follow_button==0:
        print("ERROR trying to follow from profile page")
    try:
        text = follow_button.text
    except:
        print("ERROR trying to follow from profile page")
        traceback.print_exc()  
        return 0
    if text == "Follow":
        #follow_button.click()
        try:
            driver.execute_script("arguments[0].click();", follow_button)
            return 1
        except:
            print("ERROR trying to follow from profile page")
            traceback.print_exc()  
            return 0
    else:
        print("already following this dude, next")
        return 0



def get_account_data_from_profile_page(driver):
    
   
    try:
        nb_followers_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span'
        nb_followers = driver.find_element_by_xpath(nb_followers_xpath).text
        nb_followers = treat_number(nb_followers)
        sleep(0.3)
        
        nb_followed_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a'
        nb_followed = driver.find_element_by_xpath(nb_followed_xpath).text
        nb_followed = treat_number(nb_followed)
        sleep(0.3)
        
        nb_posts_xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[1]/span/span'
        nb_posts = driver.find_element_by_xpath(nb_posts_xpath).text
        nb_posts = treat_number(nb_posts)
        sleep(0.3)
        
        username_xpath = '//*[@id="react-root"]/section/main/div/header/section/div[1]/h1'
        username = driver.find_element_by_xpath(username_xpath).text
        sleep(0.3)
        
        return username,nb_posts,nb_followers,nb_followed
    except:
        print("ERROR while getting account data")
        traceback.print_exc()  
        return None,None,None,None
    
    


def like_1st_pic(driver):
    try :
        like_button_xpath = '/html/body/div[4]/div[2]/div/article/div[2]/section[1]/span[1]/button'
        get_and_click_element(like_button_xpath,driver,click=True,
                          two_tries_with_reload=False,print_exception=False)
        return 1
    except:
        print("ERROR trying to like the 1st pic")
        traceback.print_exc() 
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
    
    
    
def get_and_click_element(xpath,driver,click=True,
                          two_tries_with_reload=True,print_exception=False):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        if click:
            element.click()
        return element
    except:
        if two_tries_with_reload:
            try:
                driver.refresh()
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if click:
                    element.click()
                return element
            except:
                if print_exception:
                    print("ERROR : get_and_click_element failure")
                    print("FYI Exception : \n")
                    traceback.print_exc()
                    print("\n")
                return 0
        else:
            if print_exception:
                print("ERROR : get_and_click_element failure")
                print("FYI Exception : \n")
                traceback.print_exc()
                print("\n")
            return 0
    
    
    









    
    
    
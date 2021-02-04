#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from instabot_data_api import dataAPI


class registeredUIComponents:
    
    '''
    In that class all the UI components that the bot might interact with, stored as class variables.
    There can be more than one xpaths for each component. In that case the API will try them out one
    by one until it can find one that corresponds to an existing element.
    '''
    
    login_email_input_field = {
        "xpaths" : ['//*[@id="loginForm"]/div/div[1]/div/label/input'],
        "description" : ""
    }
    login_password_input_field = {
        "xpaths" : ['//*[@id="loginForm"]/div/div[2]/div/label/input'],
        "description" : ""
    }
    login_accept_cookies = {
        "xpaths" : ['/html/body/div[2]/div/div/div/div[2]/button[1]'],
        "description" : ""
    }
    login_connexion_button = {
        "xpaths" : ['//*[@id="loginForm"]/div/div[3]/button/div'],
        "description" : ""
    }
    homepage_searchbar = {
        "xpaths" : ['//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/div/div/span[2]'],
        "description" : "The home search bar. Used to check that the login was successful"
    }     
    homepage_notifications_notnow = {
        "xpaths" : ['/html/body/div[4]/div/div/div/div[3]/button[2]',
                    '/html/body/div[5]/div/div/div/div[3]/button[2]'],
        "description" : "Click on not_now when asked to turn on notifications"
    }  
    homepage_save_login_infos = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/div/div/section/div/button'],
        "description" : "At the first connection (no cookies), the button to save the login infos"
    }  
    
    profile_page_followers_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span'],
        "description" : ""
    }
    profile_page_following_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a'],
        "description" : ""
    }
    first_thumbnail_photo = {
        "xpaths" : ['//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div'],
        "description" : ""
    }
    picture_carousel_account_name = {
        "xpaths" : ['/html/body/div[5]/div[2]/div/article/header/div[2]/div[1]/div[1]/span/a',
                    '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/span/a'],
        "description" : ""
    }    
    pictures_carousel_first_pic_right_arrow = {
        "xpaths" : ['/html/body/div[5]/div[1]/div/div/a'],
        "description" : ""
    }
    pictures_carousel_not_first_pic_right_arrow = {
        "xpaths" : ['/html/body/div[5]/div[1]/div/div/a[2]'],
        "description" : ""
    }
    profile_page_follow_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button'],
        "description" : ""
    }
    pictures_carousel_like_button = {
        "xpaths" : ['/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button'],
        "description" : ""
    }
    profile_page_target_nb_followers = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span',
                    '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/span/span'],
        "description" : ""
    }
    profile_page_target_nb_following = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span',
                    '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/span/span'],
        "description" : ""
    }
    profile_page_target_nb_posts = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[1]/span/span'],
        "description" : ""
    }
    profile_page_target_username = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[1]/h2'],
        "description" : "On the page of a random account, the name at the top of the page"
    }
    profile_page_target_name = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[2]/h1'],
        "description" : "On the page of a random account, the name right above the description"
    }
    profile_page_target_description = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[2]/span'],
        "description" : ""
    }    
    unfollow_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button'],
        "description" : ""
    }
    unfollow_red_button_confirm = {
        "xpaths" : ['/html/body/div[5]/div/div/div/div[3]/button[1]'],
        "description" : ""
    }
    profile_page_follow_status_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button',
                    '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div[2]/button/div',
                    '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[2]/div/div[2]/div/span/span[1]/button/div/span',
                    '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/button'],
        "description" : "the button that allows to follow or unfollow an account"        
    }

    

class UIComponentsAPI(registeredUIComponents):
    
    def __init__(self):
        pass
   
    def get(self,component,user,driver,is_warning=False):
        dataAPI().log(user,"UIAPI","INFO","try to get component : "+component)
        if is_warning == True:
            seriousness = "WARNING"
        else:
            seriousness = "ERROR"
        if component not in [i for i in dir(registeredUIComponents) if not callable(i)]:
            raise Exception("UIComponentNotRegisteredInUIAPI")
        xpaths = getattr(registeredUIComponents, component).get("xpaths")
        for xpath in xpaths:
            try :
                element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath)))
                return element
            except :
                pass
        dataAPI().log(user,"UIAPI",seriousness,"failed to access component : "+component) 
        return 0
    
    def click(self,component,user,driver,is_warning=False):
        if is_warning == True:
            seriousness = "WARNING"
        else:
            seriousness = "ERROR"
        if component not in [i for i in dir(registeredUIComponents) if not callable(i)]:
            raise Exception("UIComponentNotRegisteredInUIAPI")
        xpaths = getattr(registeredUIComponents, component).get("xpaths")
        for xpath in xpaths:
            try :
                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                break
            except :
                dataAPI().log(user,"UIAPI",seriousness,"failed to access component : "+component) 
                return 0
        try:
            element.click()       
            return 1            
        except:
            dataAPI().log(user,"UIAPI","ERROR","failed to click component : "+component) 
            return 0
            
            
    def get_text(self,component,user,driver,is_warning=False):
        element = self.get(component,user,driver,is_warning)
        if element == 0:
            return 0
        else:
            try:
                text = element.text
                return text
            except:
                dataAPI().log(user,"UIAPI","ERROR","failed get component text : "+component)
                return 0

    def get_text_and_click(self,component,user,driver):
        element = self.get(component,user,driver)
        if element == 0:
            return 0
        else:
            try:
                text = element.text
                element.click()
                return text
            except:
                dataAPI().log(user,"UIAPI","ERROR","failed to get component text + click : "+component)
                return 0

            
    def enter_text(self,component,text,user,driver):
        element = self.get(component,user,driver)
        if element == 0:
            return 0
        else:
            try:
                element.send_keys(text)
                return 1
            except:
                dataAPI().log(user,"UIAPI","ERROR","failed to enter text into component : "+component)
                return 0          
            
            
            
            
            
            
            
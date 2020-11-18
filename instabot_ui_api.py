#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class registeredUIComponents:
    
    '''
    In that class all the UI components that the bot might interact with, stored as class variables.
    There can be more than one xpaths for each component. In that case the API will try them out one
    by one until it can find one that corresponds to an existing element.
    '''
    
    login_email_input_field = {
        "xpaths" : ['//*[@id="loginForm"]/div/div[1]/div/label/input'],
    }
    login_password_input_field = {
        "xpaths" : ['//*[@id="loginForm"]/div/div[2]/div/label/input'],
    }
    login_accept_cookies = {
        "xpaths" : ['/html/body/div[2]/div/div/div/div[2]/button[1]'],
    }
    login_connexion_button = {
        "xpaths" : ['//*[@id="loginForm"]/div/div[3]/button/div'],
    }
    profile_page_followers_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span'],
    }
    profile_page_following_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a'],
    }
    first_thumbnail_photo = {
        "xpaths" : ['//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div'],
    }
    picture_carousel_account_name = {
        "xpaths" : ['/html/body/div[5]/div[2]/div/article/header/div[2]/div[1]/div[1]/span/a'],
    }    
    pictures_carousel_first_pic_right_arrow = {
        "xpaths" : ['/html/body/div[5]/div[1]/div/div/a'],
    }
    pictures_carousel_not_first_pic_right_arrow = {
        "xpaths" : ['/html/body/div[5]/div[1]/div/div/a[2]'],
    }
    profile_page_follow_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button'],
    }
    pictures_carousel_like_button = {
        "xpaths" : ['/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button'],
    }
    profile_page_target_nb_followers = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a'],
    }
    profile_page_target_nb_following = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a'],
    }
    profile_page_target_nb_posts = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/ul/li[1]/span/span'],
    }
    profile_page_target_username = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[1]/h2'],
    }
    unfollow_button = {
        "xpaths" : ['//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button'],
    }
    unfollow_red_button_confirm = {
        "xpaths" : ['/html/body/div[5]/div/div/div/div[3]/button[1]'],
    }

    

class UIComponentsAPI(registeredUIComponents):
    
    def __init__(self):
        pass
        
    def get(self,component,driver):
        if component not in [i for i in dir(registeredUIComponents) if not callable(i)]:
            raise Exception("UIComponentNotRegisteredInUIAPI")
        xpaths = getattr(registeredUIComponents, component).get("xpaths")
        for xpath in xpaths:
            try :
                element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath)))
                return element
            except :
                pass
        print("ERROR - Failed to access component : "+component)
        return 0
    
    def click(self,component,driver):
        element = self.get(component,driver)
        if element == 0:
            return 0
        else:
            try:
                element.click()
                return 1
            except:
                print("ERROR - Failed to click component : "+component)
                return 0
            
            
    def get_text(self,component,driver):
        element = self.get(component,driver)
        if element == 0:
            return 0
        else:
            try:
                text = element.text
                return text
            except:
                print("ERROR - Failed to get component text : "+component)
                return 0

    def get_text_and_click(self,component,driver):
        element = self.get(component,driver)
        if element == 0:
            return 0
        else:
            try:
                text = element.text
                element.click()
                return text
            except:
                print("ERROR - Failed to get component text + click : "+component)
                return 0

            
    def enter_text(self,component,text,driver):
        element = self.get(component,driver)
        if element == 0:
            return 0
        else:
            try:
                element.send_keys(text)
                return 1
            except:
                print("ERROR - Failed to enter text into component : "+component)
                return 0          
            
            
            
            
            
            
            
            
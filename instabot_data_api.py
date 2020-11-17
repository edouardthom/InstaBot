#!/usr/bin/env python3
# -*- coding: utf-8 -*-


########################################## Data API ##########################################

###### 1. Data API definition and objective :
# In this file is defined an API-like abstraction that positions as a layer between the user and
# the data stored under the form of CSVs.
# Its goal is to ensure a clean querying and writing of the multiple tables stored under the form of 
# CSV files in the database (here the database if simply a folder of CSVs). 
# Within the API are defined the schema (ie. column names and description) and documentation for each table.
# The API provides functions to load the tables content, add records into tables, or store new versions of 
# the tables, all this while respecting the pre-defined table schemas.

###### 2. How to use it :
### - Register a new table definition :
# In the class registeredTableDefinitions, create a new class variable. The name of the variable is the 
# name of the table definition. The value of the variable has to be a dictionary with the 
# following structure : {"description" : "Table description", "schema":{"col_1_name":"description",...}}
# There can be several tables (CSVs) following a given table definition : one per user.
# If a table follows the table definition X and stores the data for user joebiden, its name will be 
# X_joebiden, and it will be stored into the CSV file "X_joebiden.csv".
# A table cannot be managed by the API if it doesn't follow a registered table definition.
### - Call the API
# Once a table definition has been registered, there can be as many tables (CSVs) following that table definition
# as users. 
# You can : 
# - load these tables as pandas dataframe : dataAPI().get(table_definition_name,user_name)
# - add a record to any table : dataAPI().get(table_definition_name",user_name,record)
# - store a new version of the table : dataAPI().store(table_definition_name",user_name,new_table)
# You can see that for each call to the API you have to specify an existing table_definition_name
# (basically a registered table definition)


import os
import pandas as pd


class registeredTableDefinitions:
    
    '''
    In that class all the table definitions, stored as class variables.
    The name of the class variable is the name of the table definition.
    A table definitions is a table description, a list of column names and a name for each column .
    It is stored under the form of the dict with the following structure :
        {"description" : "Table description", "schema":{"col_1_name":"description",...}}
    '''
    
    follow_actions = {
    "description" : "1 new row each time the bot follows an account",
    "schema" : {
        "follow_time" : "When the account was followed by the bot",
        "account_username" : "Username of the account that the bot followed",
        "account_nb_followers" : "Number of followers of the account that the bot followed, at the moment of the follow",
        "account_nb_posts" : "Number of posts of the account that the bot followed, at the moment of the follow",
        "hashtag" : "The hashtag through which the bot found the account", 
        "first_pic_liked" : "If the first pic of the account was liked",
        "days_before_unfollowing" : "Number of days the bot follows that account - set at random at the moment of the follow",
        "unfollow_time" : "When the account was unfollowed (by the bot of by a human) - can be null"
    }}

    followers = {
    "description" : "1 new row each time the user has a new follower. \
                    Therefore, if an account follows, unfollows and then follows again, it will appear 2 times in the table.",
    "schema" : {
        "account_username" : "Username of the new follower",
        "follow_time" : "When the new follower started following",
        "unfollow_time" : "When the new follower stopped following - null if the new follower is still following"   
    }}


class dataAPI(registeredTableDefinitions):
    
    def __init__(self):
        pass
        
    def get(self,name,user):
        if name not in [i for i in dir(registeredTableDefinitions) if not callable(i)]:
            raise Exception("DataAPITableDoesntExist")
        exists = os.path.isfile(name+"_"+user+".csv")
        if exists:
            data = pd.read_csv(name+"_"+user+".csv")
        else:
            schema = getattr(registeredTableDefinitions, name).get("schema")
            columns = list(schema.keys())
            data = pd.DataFrame(columns = columns)
        return data  
    
    def add_record(self,name,user,record):
        if type(record) != dict:
            raise Exception("DataAPIInvalidRecord") 
        schema = getattr(registeredTableDefinitions, name).get("schema")
        schema_columns = list(schema.keys())
        record_columns = list(record.keys())
        record_ok = set(record_columns).issubset(set(schema_columns))
        if record_ok:
            data = self.get(name,user)
            data = data.append(record,ignore_index=True)
            data.to_csv(name+"_"+user+".csv",index=False)
        else:
            raise Exception("DataAPIInvalidRecord") 
        
    def store(self,name,user,data):
        schema = getattr(registeredTableDefinitions, name).get("schema")
        schema_columns = list(schema.keys())
        data_ok = set(data.columns).issubset(set(schema_columns))
        if data_ok:
            data.to_csv(name+"_"+user+".csv")
        else:
            raise Exception("DataAPIInvalidSchema") 
   
    
            
     
        
        
        
        
        
        
        
        


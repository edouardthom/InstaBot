#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
import numpy as np
import json
import sys

############################################################################################################
########################################### Utilities functions ############################################
############################################################################################################

def smart_sleep(seconds):
    std = 0.15*seconds
    sleep_time = np.random.normal(seconds,std)
    sleep_time = max(0.7*seconds,sleep_time)
    sleep_time = min(1.3*seconds,sleep_time)
    sleep(sleep_time)
    

def load_config_user(user,variables,config_file_name):
    """Load the config variables of a given user from the config file"""
    try:
        with open(config_file_name) as filee:
            data = json.load(filee)
    except:
        print('ERROR : configuration file "{}" not found in the current directory'.format(config_file_name))
        sys.exit()    
    try:
        data = data[user]
    except:
        print('ERROR : user "{}" not found in the config file "{}"'.format(user,config_file_name))
        sys.exit() 
    for var in variables:
        try:
            data[var]
        except:
            print('ERROR : variable "{}" not found in the config file "{}"'.format(var,config_file_name))
            sys.exit()
    return data


def load_config_variable(variable,config_file_name):
    """Load a specifif variable from the config file"""
    try:
        with open(config_file_name) as filee:
            data = json.load(filee)
    except:
        print('ERROR : configuration file "{}" not found in the current directory'.format(config_file_name))
        sys.exit()    
    try:
        variable = data[variable]
    except:
        print('ERROR : variable "{}" not found in the config file "{}"'.format(variable,config_file_name))
        sys.exit() 
    return variable    



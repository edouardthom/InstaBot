#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import os

def update_plot_data(user):
    
    ################### 1 - basic followers data ###################
    print("Updating instaedobot_follow_plot_{}.csv".format(user))
    followers = pd.read_csv("followers_{}.csv".format(user))
    followers = followers.fillna("0")
    
    followers["follow_time_by_target_hour"] = followers.follow_time_by_target.apply(lambda x:x[:13])
    
    followers["unfollow_time_by_target_hour"] = followers.unfollow_time_by_target.apply(lambda x:x[:13])
    
    
    
    follows = followers.groupby("follow_time_by_target_hour")["follow_time_by_target_hour"].agg(["count"]).reset_index()
    follows.columns = ["hour","nb_follows"]
    unfollows = followers.groupby("unfollow_time_by_target_hour")["unfollow_time_by_target_hour"].agg(["count"]).reset_index()
    unfollows = unfollows[unfollows.unfollow_time_by_target_hour != '0']
    unfollows.columns = ["hour","nb_unfollows"]
    
    
    
    
    data = follows.merge(unfollows,how="outer",on="hour").fillna(0)
    start = data.hour.min()
    stop = data.hour.max()    
    
    all_hours = pd.date_range(start,stop, freq='H')
    all_hours = pd.DataFrame({"hour":all_hours})
    all_hours['hour'] = all_hours.hour.apply(lambda x:x.strftime("%Y-%m-%d %H"))

    
    data = all_hours.merge(data,on="hour",how="left").fillna(0)
    
    data = data.sort_values("hour",ascending=True)
    data["cum_nb_of_followers"] = (data.nb_follows-data.nb_unfollows).cumsum()
    
    data.to_csv("instaedobot_follow_plot_{}.csv".format(user),index=False)
    print("DataFrame updated")
    os.system('aws s3 cp instaedobot_follow_plot_{}.csv s3://instaedobot/'.format(user))
    print("DataFrame transferred successfully to the S3 bucket for QuickSight use")
    
    ################### 2 - basic followers data ###################

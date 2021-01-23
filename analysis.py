#!/usr/bin/env python3
# -*- coding: utf-8 -*-

f = dataAPI().get("followers","edouardthegourmet")
f.columns = ["followback_time","unfollowback_time","account_username"]

data = dataAPI().get("follow_actions","edouardthegourmet")
data = data.merge(f,on="account_username",how="left")

fb = data[~data.followback_time.isnull()]

fb.account_nb_followers
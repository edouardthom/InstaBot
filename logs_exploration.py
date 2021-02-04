#!/usr/bin/env python3
# -*- coding: utf-8 -*-


################################################################################
######################################## WIP ########################################
################################################################################


# Monitoring of the bot functioning
# Monitoring of the bot actions (follows/unfollows)
# Monitoring of audience



### Exploratory lines of code, to see what went wrong in the runs
from instabot_data_api import dataAPI
import pandas as pd
import numpy as np
from utilities import list_func_calls
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
sns.set_style("whitegrid")
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

user = "edouardthegourmet"
logs = dataAPI().get("logs",user)

main = logs[logs.function == "MAIN"].reset_index(drop=True)


##################### Study of the functions #################################

functions = logs[(logs.function != "UIAPI")&
                 (logs.function != "MAIN")].reset_index(drop=True)

errors = functions[functions.seriousness=="ERROR"]

nb_logs = functions.function.value_counts().reset_index()
nb_logs.columns = ["function","tot_logs"]
nb_errors = errors.function.value_counts().reset_index()
nb_errors.columns = ["function","nb_fails"]

per_func = nb_logs.merge(nb_errors,on="function",how="left").fillna(0)
per_func.nb_errors = per_func.nb_fails.astype(int)

### Number exectutions per function
nb_exec = logs.function[logs.message == "start function"].value_counts().reset_index()
nb_exec.columns = ["function","nb_exec"]
per_func = per_func.merge(nb_exec,on="function",how="left").fillna(0)

per_func["FR"] = (100.0*per_func.nb_fails/per_func.nb_exec).apply(int)


functions_logs = logs[(logs.function != "MAIN")&
                      (logs.function != "UIAPI")&
                      (logs.function != "dataAPI")]
all_functions = np.unique(functions_logs.function)

graph = []
for func in all_functions:
    functions_called = list_func_calls(eval(func),all_functions)
    for called in functions_called:
        graph.append([func,called])
    if len(functions_called)==0:
        graph.append([func,None])
graph = pd.DataFrame(graph,columns=["function","call_function"])

graph = graph.merge(per_func,how="left",on="function")
per_call = per_func
per_call.columns = ["call_" + n for n in per_func.columns]
graph = graph.merge(per_call,how="left",on="call_function")


graph[["function","nb_exec","nb_fails","FR"]]


problematic_functions = graph[graph.FR>=10]

errors[errors.function=="follow_one_account_from_profile_page"]




##################### Study of the UIAPI logs #################################

uiapi = logs[logs.function == "UIAPI"].reset_index(drop=True)

ui_errors = uiapi[uiapi.seriousness=="ERROR"]
ui_info = uiapi[uiapi.seriousness=="INFO"]

problematic_components = ui_errors.message.apply(lambda x:x.split(":")[1][1:])
nb_fails = problematic_components.value_counts().reset_index()
nb_fails.columns = ["component","nb_fails"]

tries = ui_info.message.apply(lambda x:x.split(":")[1][1:])
tries = tries.value_counts().reset_index()
tries.columns = ["component","nb_tries"]

components = tries.merge(nb_fails,on="component",how="left").fillna(0)
components["FR"] = (100.0*components.nb_fails/components.nb_tries).apply(int)


############################## Manual checks ####################################

follow_actions= dataAPI().get("follow_actions",user)
### accounts that we supposedly are following
follow_actions[follow_actions.unfollow_time.isnull()].account_username
### accounts that we supposedly stopped following
follow_actions[follow_actions.unfollow_time.isnull()].account_username


############################## Bot actions monitoring ####################################

interval_hours = 1

follow_actions = dataAPI().get("follow_actions",user)
follow_actions = follow_actions[["follow_time","unfollow_time"]]


def transform_time(s,interval_hours):
    if type(s)==str:
        s = datetime.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")
    s = s.replace(minute=0, second=0, microsecond=0)
    hour = s.hour
    new_hour = hour-hour%interval_hours
    s = s.replace(hour=new_hour)
    return s

instants1 = follow_actions["follow_time"].apply(lambda x:transform_time(x,interval_hours))
instants2 = follow_actions["unfollow_time"].dropna().apply(lambda x:transform_time(x,interval_hours))


start_data = transform_time(min(instants1.min(),instants2.min()),interval_hours)
stop_data = transform_time(max(instants1.max(),instants2.max()),interval_hours)
nb_intervals = int((((stop_data-start_data).total_seconds())/3600)/interval_hours)

times = [start_data + datetime.timedelta(hours=interval_hours*i) for i in range(nb_intervals+1)]
times = pd.DataFrame({"time":times})

curve1 = instants1.value_counts().sort_index().reset_index()
curve1.columns = ["time","nb_follows"]
curve2 = instants2.value_counts().sort_index().reset_index()
curve2.columns = ["time","nb_unfollows"]


data = times.merge(curve1,on="time",how="left").fillna(0)
data = data.merge(curve2,on="time",how="left").fillna(0)

%matplotlib inline
figsize=(8,5)
dpi=200

fig=plt.figure(figsize=figsize,dpi=dpi)
ax = fig.add_axes([0,0,1,0.9])
 
ax.plot(data.time,data.nb_follows,color="b")
   
fmt = mdates.DateFormatter("%d %H")
ax.xaxis.set_major_formatter(fmt)
plt.show()








interval_hours = 1

data = dataAPI().get("followers",user)
instants = data[["follow_time","unfollow_time"]]

def transform_time(s,interval_hours):
    if type(s)==str:
        s = datetime.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")
    s = s.replace(minute=0, second=0, microsecond=0)
    hour = s.hour
    new_hour = hour-hour%interval_hours
    s = s.replace(hour=new_hour)
    return s

follow_times = instants["follow_time"].apply(lambda x:transform_time(x,interval_hours))
unfollow_times = instants["unfollow_time"].dropna().apply(lambda x:transform_time(x,interval_hours))


start_data = transform_time(min(follow_times.min(),unfollow_times.min()),interval_hours)
stop_data = transform_time(max(follow_times.max(),unfollow_times.max()),interval_hours)
nb_intervals = int((((stop_data-start_data).total_seconds())/3600)/interval_hours)

times = [start_data + datetime.timedelta(hours=interval_hours*i) for i in range(nb_intervals+1)]
times = pd.DataFrame({"time":times})

curve1 = follow_times.value_counts().sort_index().reset_index()
curve1.columns = ["time","new_follows"]
curve2 = unfollow_times.value_counts().sort_index().reset_index()
curve2.columns = ["time","new_unfollows"]


data = times.merge(curve1,on="time",how="left").fillna(0)
data = data.merge(curve2,on="time",how="left").fillna(0)
data["net"] = (data.new_follows - data.new_unfollows).cumsum()

### Remove 1st value
data = data.iloc[1:,:]

%matplotlib inline
figsize=(8,5)
dpi=200

fig=plt.figure(figsize=figsize,dpi=dpi)
ax = fig.add_axes([0,0,1,0.9])
 
ax.plot(data.time,data.curve1,color="g")
ax.plot(data.time,data.curve2,color="r")   

fmt = mdates.DateFormatter("%d:%m %H")
ax.xaxis.set_major_formatter(fmt)
plt.show()



### Evolution tot num. followers

%matplotlib inline
figsize=(8,5)
dpi=200

fig=plt.figure(figsize=figsize,dpi=dpi)
ax = fig.add_axes([0,0,1,0.9])
 
ax.plot(data.time,data.net,color="g")

fmt = mdates.DateFormatter("%d:%m %H")
ax.xaxis.set_major_formatter(fmt)
plt.show()





def simple_plot(data,
                title = "plz put a decent title",
                xlabel = "",
                ylabel = "",
                x_fontsize = "default",
                x_vois = [],
                x_vois_text = [],
                x_voi_just_highlight_time = [],
                x_vois_text_size = 7,
                fraction_top = 0.90,
                x_rotation = None,
                nb_max_of_x_values = "default",
                fill_under = True,
                fill_color = "lightgreen",
                curve_colors = ["deepskyblue","blueviolet","royalblue"],
                x_date_format = None,
                figsize=(8,5),dpi=200):

    """
    Plots a simple curve with some handy options.
    Particularly you can highlight x-values of interest (vois, see the parameters) 
    
    Input data :
        
        A pandas series or dataframe (if you want to plot several curves). 
        The x labels are the index.
        
        Example data :
            
        data = pd.Series([1,2,3,4],index=["a","b","c","d"])
        data = pd.Series([1,2,3,4],index=[3,5,7,9])
        data = pd.DataFrame({"airbnb":[2,3,4,5],"booking":[1,4,6,9]})
        
    Parameters :
        
        x_vois : the x-values that you want to highlight. The corresponding y-values will
        also be highlighted
        x_vois_text : for each x_voi, some comments you might want to add
            Example : highlight the median of a distribution
            Caveat : this highlighting works only for input series with a numerical index. 
            Besides, the x_vois must be present in the index of the input series.
            
        fill_between : if you want to fill under the curve with a color
            Caveat : works only with a series as input (only 1 curve)
        
    """
    import seaborn as sns
    sns.set_style("whitegrid")
    if type(data) != pd.Series and type(data) != pd.DataFrame:
        print("Please input a pandas series or dataframe.")
        return 0

    ### Try to convert the index to datetime (if it's not a date nothing happens)
    dates = pd.Series(data.index.values).apply(try_convert_sth_to_datetime)
    data.index = dates
    
    ### Create the figure and the axis
    fig=plt.figure(figsize=figsize,dpi=dpi)
    ax = fig.add_axes([0,0,1,fraction_top])
    
    ### Plot
    if type(data)==pd.DataFrame:
        columns = data.columns
        for i,c in enumerate(columns):
            ax.plot(data.index,data[c].reset_index(drop=True),color=curve_colors[i])
        plt.legend()
    else:
        ax.plot(data.index,data.values,color=curve_colors[0])
    
    ### Title and x/y labels
    plt.suptitle(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    ### If the index is composed of dates, above it was converted to datetime
    # The part of code below formats them so they are displayed in the desired way
    # Example : "%B %d"
    if x_date_format:
        fmt = mdates.DateFormatter(x_date_format)
        ax.xaxis.set_major_formatter(fmt)
    
    ### Possibly fill color under the curve
    if fill_under:
        ax.fill_between(data.index,data.values,color=fill_color,alpha=0.7)

    ### This locator puts x ticks at regular intervals, in a limited number
    if nb_max_of_x_values != "default":
        loc = matplotlib.ticker.MaxNLocator(nbins=nb_max_of_x_values) 
        ax.xaxis.set_major_locator(loc)
    
    ### Modify the xticklabels : fontsize and rotation
    for tick in ax.xaxis.get_major_ticks():
        if x_fontsize!="default":
            tick.label.set_fontsize(x_fontsize)
        if x_rotation:
            tick.label.set_rotation(x_rotation)
            
    ### Display the x values of interest
    ax_height = ax.get_ylim()[1] - ax.get_ylim()[0]
    ax_width = ax.get_xlim()[1] - ax.get_xlim()[0]

    for i,x_voi in enumerate(x_vois):
        if x_voi in data.index:
            y_voi = data[x_voi]
            text = x_vois_text[i]
            rect = matplotlib.patches.Rectangle((0,y_voi), x_voi, 0.001*ax_height, angle=0.0, color="navy")
            ax.add_patch(rect)
            rect2 = matplotlib.patches.Rectangle((x_voi,0), 0.001*ax_width, y_voi, angle=0.0, color="navy")
            ax.add_patch(rect2)
            matplotlib.pyplot.text(x = (0.05*ax_width) + ax.get_xlim()[0], 
                                   y = y_voi+0.02*ax_height , 
                                   s=text, fontsize=x_vois_text_size)
        else:
            print("This x-value of interest : "+str(x_voi)+" is not in the input data index.")
            
    for time,text in x_voi_just_highlight_time:
        if time in data.index:
            time_mdate = mdates.date2num(time)
            rect = matplotlib.patches.Rectangle((time_mdate,0), 0.001*ax_width, ax_height, angle=0.0, color="navy", 
                                                alpha = 0.5)
            ax.add_patch(rect)
            matplotlib.pyplot.text(x = time_mdate+0.005*ax_width, 
                                   y = 0.97*ax_height , 
                                   s=text, fontsize=x_vois_text_size)            

    sns.set_style("whitegrid")
    plt.show()


















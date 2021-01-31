#!/usr/bin/env python3
# -*- coding: utf-8 -*-


################################################################################
######################################## WIP ########################################
################################################################################



### Exploratory lines of code, to see what went wrong in the runs
from instabot_data_api import dataAPI
import re
import pandas as pd
import numpy as np
from instabot_functions import *

user = "edouardthegourmet"
logs = dataAPI().get("logs",user)
logs = logs[logs.function!="update_followers"]


main = logs[logs.function == "MAIN"].reset_index(drop=True)
uiapi = logs[logs.function == "UIAPI"].reset_index(drop=True)
functions = logs[(logs.function != "UIAPI")&
                 (logs.function != "MAIN")].reset_index(drop=True)

errors = logs[logs.seriousness=="ERROR"]

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


graph[["function","nb_exec","nb_fails"]]


problematic_functions = np.unique(graph[graph.FR>=20].function)

f = "follow_accounts_from_hashtag"
f = graph[graph.function == f]
f.call_FR

f.nb_exec

f[["call_function","call_nb_exec","call_nb_fails"]]

errors[errors.function == "get_account_data_from_profile_page"]

errors[errors.function == "follow_one_account_from_profile_page"]


uiapi = errors[errors.function=="UIAPI"]
problematic_components = uiapi.message.apply(lambda x:x.split(":")[1][1:])
problematic_components.value_counts()




import dis
def list_func_calls(fn,the_functions):
    """
    Takes as input a function name (fn) and get all its calls to other functions
    Returns only the ones that appear in the list the_functions
    """
    funcs = []
    bytecode = dis.Bytecode(fn)
    instrs = list(reversed([instr for instr in bytecode]))
    for (ix, instr) in enumerate(instrs):
        if instr.opname=="CALL_FUNCTION":
            load_func_instr = instrs[ix + instr.arg + 1]
            funcs.append(load_func_instr.argval)
            
    funcs = [f for f in funcs if f in the_functions]
    return funcs

















errors.function.value_counts()

errors[errors.function=="unfollow_one_account"]

sel = logs.iloc[160:188]
sel[["function","seriousness"]]
sel.message.loc[170]

start = 170
stop = 210
for n in range(start,stop):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(logs[["function","seriousness","message"]].loc[n])
        print("\n")






with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(logs)




email
password

log_in(email,password,user,use_cookies=True,headless=False,for_aws=False)











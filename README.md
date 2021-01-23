# InstaBot 🤖  
    
### Instagram audience expansion and monitoring  
  
[Features](#part1)  
[Get started with the bot - tutorial](#part2)  
[Next steps](#part3)  
[Code organisation](#part4)   
   
## Features :  
* automatically interact with accounts in a smart way to maximise the number of followers 
* provide reporting data regarding both the audience evolution and the interaction strategy 
* communicate insights based on that data  
   
**More concretely, what does the bot (MVP) do ?**  
* follow random accounts (found through hashtags, or from the followers list of some accounts)   
* after some time, unfollow them, to avoid following too many people at the same time
* while performing this follow-unfollow process, supdate datasets regarding both the actions (who he followed, unfollowed,...), and the audience of the account (mainly who followed and unfollowed the user).  
* this data is stored in CSV files accessible in a database folder if you wish to analyse them  
* the bot uses that data to regularly send emails containing relevant insights.  
* he also allows you to monitor the run : logs are stored in the database, and bug reports can regularly be sent via email.  
    
## Get started with the bot - tutorial  
#### 1. Set-up the environment 
You need :  
* Python 3.7
* Python packages : Selenium, Pandas, Numpy.  
* Google Chrome. Check the version you have within Chrome : menu->Help->About.
* Chrome driver that suits your version of Chrome. You can download it here : https://chromedriver.chromium.org/downloads. Then you need to make it findable by Selenium. On MacOS, as an example, I put it in the folder */usr/local/bin*.  
#### 2. Run the bot
* Clone this repository in a cosy location : `git clone https://github.com/edouardthom/InstaBot.git`
* Navigate to the instabot folder `cd InstaBot`  
* Fill *config.json* with the values of your choice, and save.  
* Finally, run `python instabot_main.py [account_username]` and let the bot do its job      
  
If you run in a terminal, you will be able to follow what the bot is doing with the logs :  
  
![Alt text](/documentation/screenshot_terminal.png?raw=true)  
  
Every morning and evening you will receive a polite email containing insights (parameters in config.xml) :  

![Alt text](/documentation/screenshot_insights_email.png?raw=true)   
  
You'll also receive bug reports :  

![Alt text](/documentation/screenshot_bug_report.png?raw=true)  
   
#### About the data generated  
The bot (MVP) generates 3 datasets at the moment (including the one containing the logs).
The datasets are stored as csv in the *InstaBot/database* folder.  
The schema and description of each dataset is defined in the class *registeredTableDefinitions* in the *instabot_data_api.csv* file. There you can see exactly what data the bot outputs, and what it contains.
#### About the maintenance  
The bot is designed to overcome minor errors and keep running. From time to time it can crash but that should remaine relatively rare.    
It is a good practice to regularly have a look at the logs to spot recurring minor errors and fix them.  
By default the logs will be printed, and be stored in * InstaBot/database/logs_X.csv* for user X.  
Bug reports will be sent as well via email.  
One specific kind of eror occurs when the bot fails to interact (click, enter text,...) with the Instagram UI. It often happens when the source code of Instagram changed, and the bot cannot find a component (button,...) anymore.  
The UI API (*instagram_ui_api.py*) ensures a frictionless management of the interactions with the UI. All components that the bot interacts with are declared in the *registeredUIComponents* class.  
If you see often logs like "failed to click component X" , you might need to update its xpath in the class *registeredUIComponents* in *instabot_ui_api.py*.
   
## Next steps
The bot is currently running on several accounts, gathering data.   
Next : leverage the data produced by the bot for audience targetting.
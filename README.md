# InstaBot 🤖  
  
*Documentation in progress - Nov 2020*
  
### Instagram audience expansion and monitoring  
  
[Features](#part1)  
[Get started with the bot - tutorial](#part3)  
[Technical requirements](#part2)  
[Code organisation](#part4)  
   
## Features :  
* automatically interact with accounts in a smart way to maximise the number of followers 
* provide reporting data regarding both the audience evolution and the interaction strategy 
* communicate insights based on that data  
**More concretely, what does the bot (MVP) do ?**  
Once given access to an Instagram account, he follows random accounts, that he finds through the list of hashtags you provided him beforehand.  
The hope is to be followed-back by a portion of these accounts.  
After some (random) time, he will unfollow them, to prevent the account from following too many people.  
While performing this follow-unfollow process, he makes sure to store and update datasets (csv files) regarding both his actions (who he followed, unfollowed, their characteristics like # of posts/followers..., picture liked...), and the audience of the account (mainly who followed and unfollowed the account).  
This high-quality data is easily accessible in a database folder if you want to analyse it. You can check for example the characteristics of the accounts who follow-back the most, or the hashtags that work the best to get follow-backs.  
Besides, the bot uses that data to regularly send emails containing relevant insights.  
Last techy thing : to allow you to monitor the run, logs are stored in the database, and bug reports can regularly be sent via email.  
  
*Performances : as of Nov 20, on my 2017 macbook pro 13,  the bot properly run days without crashing :))*
  
## Get started with the bot - tutorial  
You need :  
* Python 3.7
* Python packages : Selenium, Pandas, Numpy. I recommend conda : you can create a virtual env. with Python 3.7 and install these packages.
* Google Chrome
* Chrome driver that suits your version of Chrome. You can download it here : https://chromedriver.chromium.org/downloads. Then you need to make it findable by Selenium. On MacOS, as an example, I put it in the folder */usr/local/bin*.
Once the 4 ingredients above are well set-up : 
* Clone this repository in a cosy location
* Navigate to the instabot folder (InstaBot)
* fill *instabot_running_variables.py* with the values of your choice. Be particularly careful with the variable *nb_hashtags_per_loop* and *nb_follows_per_hashtag*. They will determine how many accounts the bot will follow at every loop (one loop every *time_between_loops* seconds). You shouldn't follow more than 20 accounts per hour if you don't want your account to get blocked by Instagram.  
* Then simply run  *instabot_main.py* and let the bot do its job. You should see the logs being printed out so you can follow the bot work.   
#### About the data generated  
The data is managed within the code by the DataAPI (*instabot_data_api.csv*). It is useful to enforce data quality and bring clarity regarding what the data contains (more info next section).
The schema and description of each dataframe is defined in the class *registeredTableDefinitions* in the dataAPI file. There you can see exactly what data the bot outputs, and what it contains.
#### About the maintenance  
The bot is designed to run even if if faces some unforeseen events. However it can still crash. In that case you will need to look into the logs.  
By default the logs will be both printed, and be stored in *database_path/logs_X.csv* for user X.  
Regarding the xpaths of the diverse compoments (buttons, textboxes) the bots will interact with (get text, click, enter text), they are all listed in the *instabot_ui_api.py*. It is yet another API, this time to manage efficiently  the paths to the components.  
If you see often logs like "failed to click component" relative to the same component, you might need to update its xpath in the class registeredUIComponents in *instabot_ui_api.py*.
   
## Technical requirements    
* (MVP) Autonomy and robustness 
  * Should be able to run continuously and rarely crash 
* (MVP) Low maintenance efforts  
  * make it frictionless to ensure that the code keeps up with Instagram UI changes 
  * efficient logs management
* (MVP) Environment-agnostic  
  * The bot should be able to run on usual platforms : raspberry Pi, AWS instance, classic desktop...
  * Only prerequisite : Python, Selenium, Chrome+Driver
* (MVP) Output good-quality data  
  * transparency and clarity over what the data contains  
  * guarantee the quality of that data 
* (MVP) Send emails containing relevant insights
  * Grab and process the data to get insights
  * Ship these insights to whoever is interested via email
* (MVP) Multi-account support
  * The bot should be able to run for several different Instagram accounts in parallel.
   
* (2.0) Display relevant insights in a real-time dashboard easily accessible
  * This should provide more granular insights that a daily email newsletter
* (2.0) Possibility to optimise the interactions strategy to maximise certain metrics, using past data 
  * Diverse techniques can be employed to make the most of historical data to optimise the bot interactions (follows, likes,comments) , in order to maximise metrics such as the number of followers or their loyalty. We can think of the bot making the decision to follow a certain account based on a score given by a ML model.
* (2.0) Audience targetting
  * Gain followers that are part of a target audience
      
## Code organisation   
The central piece of the bot is the while(1) loop that you can find in *instabot_main.py*.  
Here is the structure of the code with the interactions between the diverse parts :  
   
![Alt text](/documentation/code_structure.png?raw=true "Structure of the code")
     
#### About the data API  
See the objectives and the documentation in the file "instabot_data_api.py"
    

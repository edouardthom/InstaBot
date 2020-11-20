# InstaBot 🤖  
  
*Documentation in progress - Nov 2020*
  
### Instagram audience expansion and monitoring  
  
[Features](#part1)  
[Technical requirements](#part2)  
[Get started with the bot](#part3)  
[Code organisation](#part4)  
   
## Features :  
* automatically interact with accounts in a smart way to maximise the number of followers 
* provide reporting data regarding both the audience evolution and the interaction strategy 
* communicate insights based on that data
   
## Technical requirements    
* (MVP) Autonomy and robustness 
  * Should be able to run continuously and rarely crash 
* (MVP) Environment-agnostic  
  * The bot should be able to run on usual platforms : raspberry Pi, AWS instance, classic desktop...
  * Only prerequisite : Python, Selenium, Chrome+Driver
* (MVP) Low maintenance efforts  
  * make it frictionless to ensure that the code keeps up with Instagram UI changes 
  * efficient logs management
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
   
## Get started with the bot   
You need :  
* Python 3.7
* Python packages : Selenium, Pandas, Numpy. I recommend conda : you can create a virtual env. with Python 3.7 and install these packages.
* Google Chrome
* Chrome driver that suits your version of Chrome. You can download it here : https://chromedriver.chromium.org/downloads. Then you need to make it findable by Selenium. On MacOS you can put it in the folder */usr/local/bin* for example.
Once the 4 ingredients above are well set-up, fill *instabot_running_variables.py* with the values of your choice. Be careful not to follow more than 20 accounts per hour if you don't want your account to get blocked by Instagram.  
You can then run *instabot_main.py* and let the bot do its job. It should be relatively robust, but expect some failures here and there (MVP - Nov. 2020).   
#### About the data generated  
The data is managed within the code by the DataAPI (*instabot_data_api.csv*). It is useful to enforce data quality and bring clarity regarding what the data contains (more info next section).
The schema and description of each dataframe is defined in the class *registeredTableDefinitions* in the dataAPI file. There you can see exactly what data the bot outputs, and what it contains.
#### About the maintenance  
The bot is designed to run even if if faces some unforeseen events. However it can still crash. In that case you will need to look into the logs.  
By default the logs will be both printed, and be stored in *database_path/logs_X.csv* for user X.  
Regarding the xpaths of the diverse compoments (buttons, textboxes) the bots will interact with (get text, click, enter text), they are all listed in the *instabot_ui_api.py*. It is yet another API, this time to manage efficiently  the paths to the components.  
If you see often logs like "failed to click component" relative to the same component, you might need to update its xpath in the class registeredUIComponents in *instabot_ui_api.py*.
   
## Code organisation   
The central piece of the bot is the while(1) loop that you can find in *instabot_main.py*.  
Here is the structure of the code with the interactions between the diverse parts :  
   
![Alt text](/code_structure.png?raw=true "Structure of the code")
     
#### About the data API  
See the objectives and the documentation in the file "instabot_data_api.py"
    

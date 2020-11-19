# InstaBot  

### Instagram audience expansion and monitoring

## Features :  
* automatically interact with accounts in a smart way to maximise the number of followers 
* provide reporting data regarding both the audience evolution and the interaction strategy 
* communicate insights based on that data

## Technical requirements :  
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
   
*Version 1.0 - Work In Progress*

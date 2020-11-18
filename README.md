# InstaBot 
**Version 1.0 - Work In Progress**

InstaBot (1.0) focuses on Instagram audience expansion.

Features :  
* automatically interact with accounts in a smart way to maximise the number of followers 
* provide reporting data regarding both the audience evolution and the interaction strategy 
* communicate insights based on that data

Technical requirements :  
* Ability to run continuously  
  * The bot is started once per user, and keeps doing its job as well as possible until being instructed otherwise. 
* Environment-agnostic  
  * The bot should be able to run on usual platforms raspberry Pi, an AWS instance, a classic desktop... Basically don't rely on proprietary services, such as for example Amazon SES to send emails, that runs only on AWS.
* Low maintenance efforts  
  * make it frictionless for the code to keep up with Instagram UI changes 
  * efficient logs management
* Output good-quality data  
  * transparency and clarity over what the data contains  
  * guarantee the quality of that data 
* Send emails containing relevant insights
  * Grab and process the data to get insights
  * Ship these insights to whoever is interested via email

* (2.0) Display relevant insights in a real-time dashboard easily accessible
  *This should provide more granular insights that a daily email newsletter
* (2.0) Possibility to optimise the interactions strategy to maximise certain metrics, using past data 
  *Diverse techniques can be employed to make the most of historical data to optimise the bot interactions (follows, likes,comments) , in order to maximise metrics such as the number of followers or their loyalty. We can think of the bot making the decision to follow a certain account based on a score given by a ML model.

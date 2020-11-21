############ The variables that the boot needs to run ############
 
# The path to the folder that will contain the data (the CSV files)
database_path = "/Users/ethomas/Instabot/database/"

user = "edouard_thom"
user_email = 'edouard.thom@gmail.com'
password = ''

# The hastags thanks to which the bot will find users to follow
hashtags = ["instalife","friends","beach","ski","followeraktif","follower4follower",
            "instagood","followme","selfie","foodie",
            "car","clothing","followers","like4like","f2f","l4l",
            "followforfollow","followback","followbackinstantly","tagblender","followmefollowyou",
            "followbackteam","followmeback","followbackalways","f4f",
            "homemade","iliketurtles","followstagram",
            "fresh","foodporn","cute","me","igdaily",
            "doglovers","rockstar","sharefood","photooftheday","instadaily"]

# How often the main while(1) loop will run
time_between_loops = 3600

# During one loop, number of hashtags that the bot will search for, and for each how
# many accounts it will follow
# Be aware that Instagram blocks accounts that follow too much.  
nb_hashtags_per_loop = 7 
nb_follows_per_hashtag = 3


########## About Emails ##########

# The gmail account from which the bot can send the emails
BOT_GMAIL_ADDRESS = 'instabot.insights@gmail.com'
BOT_GMAIL_PASSWORD = ''

# How often the bot sends insights emails 
time_between_insights_emails = 3600*2
# The basic insight emails sum-up to the user what happened over the past few hours
email_hours_back = 2

# Authorize the sending of maintenance emails
send_maintenance_emails = True

# Developer email address = for maintenance emails
dev_email = 'edouard.thom@gmail.com'

# How often the bot sends maintenance emails 
time_between_maintenance_emails = 3600*3
# The basic insight emails sum-up to the developer the errors that occurred over the past few hours
email_hours_back = 3
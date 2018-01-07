# Khan-Academy-Homework-Checker

This project detects if my sister has done her studying khan academy for the day and remind her to do it if not. It will also tell my mom what my sister has and hasn't done on Khan Academy for the day, and remind her to remind my sister to do her studying. Might include functionality like automatically emailing myself if she hasn't done it as well. It will be using the [khan academy api](https://github.com/Khan/khan-api) as well as some internal apis used by khanacademy.org. This is allowed as per the README in the khan academy api repository

### High-Level Application Flow

1. Application will attempt to perform the OAuth1.0 workflow (khan academy does not have 2.0 implemented)
	* If the auth tokens are not cached, the program performs an automated login via the selenium package and the retrieved auth tokens are cached. The credentials needed to perform the login are in a `.credentials.json` file. (Description coming soon).
	* If the cached auth tokens exist, they are used to make the khan academy api calls.

2. Application retrieves data pertaining to how much time my sister has spent watching videos today as well as how many problems she has gotten correct today
3. This information will be compared against threshold values (60 minutes of video watching and 15 problems correct) 
4. If she hasn't surpassed the threshold values, a text message is sent to her phone and my mom's detailing what she has left to complete

### System Requirements
1. python3 and all packages in requirements.txt installed
2. [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) downloaded and in your path as well as its dependencies. On Debian these can be installed via `sudo apt install libgconf-2-4 libnss3-dev`. Visit this [stackoverflow post](https://askubuntu.com/questions/510056/how-to-install-google-chrome) to learn how to install chrome (dep for chromedriver)
3. A valid .credentials.json file in the working directory of the project (description coming soon)
4. A configured default AWS profile on the system

### `.credentials.json` file
The following keys are required: 
1. `email`: email of student khan academy account
2. `password`: password of student khan academy account
3. `student_number`: the phone number of the student to send reminders to
4. `parent_number`: the phone number of the parent to send reminders to
5. `consumer_key`: the consumer key you get after enabling the khan academy api (See the [Khan Academy register an app page](https://www.khanacademy.org/api-apps/register) to get this)
6. `consumer_secret`: the consumer secret you get when you enable the khan academy api

The reason I needed to include `email` and `password` in the file is so that the program can run in a completely automated fashion. I have it running as a cron job twice a day on an EC2 instance so that it reminds my mom and sister to do her khan academy work. In the case of any failure with cached OAuth tokens, it will perform an automated login. 

I plan to create a fork of this repository that includes only manual OAuth authentication, caching the tokens received (as this code already does), and adding support for multiple users to create reminders/alerts for their child doing their work on khan academy. In general I plan to make the fork much more user friendly; I'll probably wrap the functionality in a web application.

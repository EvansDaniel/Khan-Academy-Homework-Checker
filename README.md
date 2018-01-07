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
2. [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) downloaded and in your path as well as its dependencies. On Debian these can be installed via `sudo apt install libgconf-2-4 libnss3-dev`
3. A valid .credentials.json file in the working directory of the project (description coming soon)
4. A configured default AWS profile on the system

# Reddit-Space_Launches
 
### This is a bot designed to create a stickied post when a space launch is scheduled within the next 24 hours.
- Runs daily, stikies posts with relevant info
- Uses a timedelta of 24 hours. 
- Logs stickied post ID and unstickes the next morning
- Logging is sent through a Discord Webhook. 

# Setup

## Setup a Linux Host
I'm using Ubuntu LTS on an Oracle Cloud VM. There are free-tiers available as of today. Google Compute and Amazon AWS are similar products. You can also roll your own host with an old PC or a Raspberry Pi. You'll need to know a bit of Linux CLI or you'll need to be ready to learn! Run these commands through the CLI.

## Setup Git
1. [Create a Github account.](https://github.com/join)

2. [Go here and install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) if you don’t have it already.

3. [Assuming you're reading this on the repo page](https://github.com/SaltySOMAdmin/Reddit-Space_Launches), select ‘fork’ to create a copy of it to your Github account. 

4. From your new repo, select **Code** and then under **Clone** copy the HTTPS URL (e.g. https://github.com/SaltySOMAdmin/Reddit-Space_Launches.git) to download a local copy

5. Navigate to a folder you want a local copy of the repo to live, and clone the Github repo to your host:
   1. It's up to you where to put the repo - recommended in a folder like /home/YourUserAcct/Github/ or /home/YourUserAcct/. Once you clone the directory it will create a subfolder with the name of your fork.
   2. git clone `<url>`
      1. e.g. git clone https://github.com/SaltySOMAdmin/Reddit-Space_Launches.git

## Install necessary software prerequisites: 

1.  Install Python3

		sudo apt install python3

2.  Create a python virtual environment in a directory

		/usr/bin/python3 -m venv /home/ubuntu/Reddit-Space_Launches

3.  Use the virtual python3 environment

		source /home/ubuntu/Reddit-Space_Launches/bin/activate

4.  Install PIP Prereqs

		pip3 install requests pytz praw
	
5.  Setup Discord Webhook - Right click the channel in Discord --> Edit Channel --> Integrations --> Create Webhook. Paste your webhook into webhook.txt. (webhook="http://yourURL")
	
		sudo nano /home/ubuntu/Reddit-Space_Launches/webhook.txt


## Configure the script.
- There are several sections you need to customize in the main script (SpaceLaunches.py).

- Logging paths, subreddit_name, and config.py will need to be updated with your credentials. 

## Crontab Settings
This is where you will set your schedule to run. My script runs every Sunday. To open your cron settings type this into your terminal: crontab -e

- Run main script

		0 7 * * 0 /bin/bash -c "source /home/ubuntu/Reddit-Space_Launches/bin/activate && python3 /home/ubuntu/Reddit-Space_Launches/SpaceLaunches.py" >> /home/ubuntu/Reddit-Space_Launches/cron_log.txt 2>&1
		0 6 * * 0 /bin/bash -c "source /home/ubuntu/Reddit-Space_Launches/bin/activate && python3 /home/ubuntu/Reddit-Space_Launches/unsticky_old_posts.py" >> /home/ubuntu/Reddit-Space_Launches/cron_log.txt 2>&1

- Upload logs after
		10 7 * * * /home/ubuntu/Reddit-Space_Launches/forward_cron_log.sh
		15 7 * * * /home/ubuntu/Reddit-Space_Launches/forward_error_log.sh

## Setup Continuous Deployment with Github Actions

Allows you to deploy your code via Github vs logging into the VPS and updating the code/uploading a new file. Allows for easier collaboration as well. I followed a guide similar to this one:
https://docs.github.com/en/actions/use-cases-and-examples/deploying/deploying-with-github-actions

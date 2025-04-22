import requests
import praw
import config  # Your config file with credentials
import logging
from datetime import datetime, timedelta, timezone
import pytz

# Set up logging
logging.basicConfig(
    filename='/home/ubuntu/Reddit-Space_Launches/error_log.txt',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Reddit API setup
reddit = praw.Reddit(
    client_id=config.destination_client_id,
    client_secret=config.destination_client_secret,
    password=config.destination_password,
    username=config.destination_username,
    user_agent=config.destination_user_agent
)

subreddit_name = 'UFOs_Archive'
LAUNCH_API_URL = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
LOOKAHEAD_HOURS = 24

def get_launches_within_24_hours():
    try:
        response = requests.get(LAUNCH_API_URL)
        response.raise_for_status()
        launches = response.json().get("results", [])
        now_utc = datetime.now(timezone.utc)
        cutoff = now_utc + timedelta(hours=LOOKAHEAD_HOURS)
        
        upcoming = []
        for launch in launches:
            net_str = launch.get("net")
            if net_str:
                net_time = datetime.fromisoformat(net_str)
                if now_utc < net_time <= cutoff:
                    upcoming.append(launch)
        return upcoming
    except Exception as e:
        logging.error("Failed to get launch data: %s", str(e))
        return []

def build_post_body(launches):
    body = "Here are the launches scheduled in the next 24 hours:\n\n"
    for launch in launches:
        name = launch.get('name', 'Unknown')
        time = launch.get('net', 'Unknown')
        provider = launch.get('launch_service_provider', {}).get('name', 'Unknown')
        mission = launch.get('mission', {}).get('name') if launch.get('mission') else 'N/A'
        vid_url = launch.get('vidURLs', ['Not available'])[0]
        info_url = launch.get('url', '')
        
        body += f"---\n\n"
        body += f"🚀 **{name}**\n"
        body += f"**Provider**: {provider}\n"
        body += f"**Mission**: {mission}\n"
        body += f"**Launch Time (UTC)**: {time}\n"
        body += f"**Webcast**: {vid_url}\n"
        body += f"[More Info]({info_url})\n\n"
        
    return body

def post_to_reddit(launches):
    try:
        if not launches:
            print("No launches to post.")
            return

        eastern = pytz.timezone('US/Eastern')
        today_eastern = datetime.now(eastern).strftime("%B %d, %Y")
        title = f"🚀 Upcoming Launches for {today_eastern}"

        body = build_post_body(launches)
        submission = reddit.subreddit(subreddit_name).submit(title, selftext=body)
        submission.mod.sticky()
        with open('/home/ubuntu/Reddit-Space_Launches/stickied_log.txt', 'a') as f:
            f.write(f"{submission.id}\n")
        print("Posted and stickied:", title)
    except Exception as e:
        logging.error("Failed to post to Reddit: %s", str(e))

def main():
    launches = get_launches_within_24_hours()
    post_to_reddit(launches)

if __name__ == "__main__":
    main()

import requests
import praw
import config  # Your config file with credentials
import logging
from datetime import datetime, timedelta, timezone
import re
import unicodedata
from zoneinfo import ZoneInfo

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
FLAIR_ID = 'aa9bb36e-203f-11f0-9c87-1ada177873d9'  # Space Launch

def clean_text(text):
    if not text:
        return ''
    text = unicodedata.normalize('NFKC', str(text))
    text = re.sub(r'[\u200B-\u200D\uFEFF\u2060-\u206F\x00-\x1F\x7F]', '', text)
    return re.sub(r'([\\`*_{}\[\]()#+!])', r'\\\1', text)  # Removed the \- from this line


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

def format_launch_time(utc_time_str):
    try:
        utc_dt = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        eastern = ZoneInfo("America/New_York")
        est_dt = utc_dt.astimezone(eastern)
        return f"{utc_dt.strftime('%Y-%m-%d %H:%M')} UTC / {est_dt.strftime('%I:%M %p %Z')}"
    except Exception as e:
        logging.error("Failed to format launch time: %s", str(e))
        return utc_time_str  # fallback

def build_post_body(launches):
    body = "**Here are the launches scheduled for the next 24 hours:**\n\n"
    for launch in launches:
        name = clean_text(launch.get('name', 'Unknown'))
        time = launch.get('net', 'Unknown')
        formatted_time = clean_text(format_launch_time(time))
        provider = clean_text(launch.get('launch_service_provider', {}).get('name', 'Unknown'))
        mission = clean_text(launch.get('mission', {}).get('name') if launch.get('mission') else 'N/A')
        vid_url = clean_text(launch.get('vidURLs', ['Not available'])[0])
        info_url = launch.get('url', '')

        body += f"---\n\n"
        body += f"- **{name}**\n"
        body += f"**Provider:** {provider}\n"
        body += f"**Mission:** {mission}\n"
        body += f"**Launch Time:** {formatted_time}\n"
        body += f"**Webcast:** {vid_url}\n"
        body += f"[More Info]({info_url})\n\n"

    body += f"---\n\n\n"
    body += f"**Visit [RocketLaunch.Live](https://www.rocketlaunch.live) to view the full schedule for future planned launches.**\n\n"
    body += f"**For more information about how to identify space launches and their effects, check out our [Space Launches Wiki Page.](https://www.ufos.wiki/investigation/space-launches/)**\n"
    return body

def post_to_reddit(launches):
    try:
        if not launches:
            print("No launches to post.")
            return

        eastern = ZoneInfo("America/New_York")
        today_eastern = datetime.now(eastern).strftime("%B %d, %Y")
        title = f"🚀 Upcoming Rocket Launches for {today_eastern}"

        body = build_post_body(launches)
        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit(title, selftext=body)

        submission.flair.select(FLAIR_ID)

        stickied_posts = [post for post in subreddit.hot(limit=10) if post.stickied]
        if len(stickied_posts) < 2:
            try:
                submission.mod.sticky()
            except Exception as e:
                logging.error("Attempted to sticky but failed: %s", str(e))
        else:
            print("Sticky slots full. Post not stickied.", today_eastern)
            try:
                already_replied = any(
                    "launch alert could not be stickied" in c.body.lower()
                    for c in submission.comments
                )
                if not already_replied:
                    submission.reply(
                        "This launch alert could not be stickied — both sticky slots are currently in use."
                    )
            except Exception as comment_error:
                logging.error("Failed to comment fallback sticky note: %s", str(comment_error))

        with open('/home/ubuntu/Reddit-Space_Launches/stickied_log.txt', 'a') as f:
            f.write(f"{submission.id}\n")

        print("Posted:", title)
    except Exception as e:
        logging.error("Failed to post to Reddit: %s", str(e))

def main():
    launches = get_launches_within_24_hours()
    post_to_reddit(launches)

if __name__ == "__main__":
    main()

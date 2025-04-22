import praw
import config
import logging

# Logging setup
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

log_path = '/home/ubuntu/Reddit-Space_Launches/stickied_log.txt'

def unsticky_logged_posts():
    try:
        with open(log_path, 'r') as f:
            post_ids = [line.strip() for line in f if line.strip()]

        for post_id in post_ids:
            try:
                submission = reddit.submission(id=post_id)
                submission.mod.sticky(state=False)
                print(f"Unstickied post: {post_id}")
            except Exception as e:
                logging.error(f"Failed to unsticky post {post_id}: {e}")

        # Clear log file after unsticking
        open(log_path, 'w').close()

    except Exception as e:
        logging.error(f"Failed to read stickied_log.txt: {e}")

if __name__ == "__main__":
    unsticky_logged_posts()

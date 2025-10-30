import praw
import os
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# Load API keys from .env
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = "pennyai:v0.1 (by u/Effective-Task347)"


def fetch_reddit_posts(output_path, limit_per_sub=100, subreddit_list=None):
    if subreddit_list is None:
        subreddit_list = ["pennystocks"]  # default single subreddit

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    all_posts = []

    for sub_name in subreddit_list:
        subreddit = reddit.subreddit(sub_name)
        print(f"\nFetching from r/{sub_name}...")
        for post in tqdm(subreddit.new(limit=limit_per_sub), desc=f"r/{sub_name} posts"):
            post.comments.replace_more(limit=0)
            comments = [c.body for c in post.comments[:10]]  # Top 10 comments

            all_posts.append({
                "subreddit": sub_name,
                "id": post.id,
                "title": post.title,
                "body": post.selftext,
                "author": str(post.author),
                "score": post.score,
                "num_comments": post.num_comments,
                "comments": comments,
                "created_utc": post.created_utc,
                "url": post.url
            })
    all_posts = pd.DataFrame(all_posts)
    all_posts.to_parquet(
        output_path, engine="pyarrow", index=False)

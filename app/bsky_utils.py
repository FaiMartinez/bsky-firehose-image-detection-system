import os
from atproto import Client
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

def login_bsky():
    import os
    from atproto import Client
    from dotenv import load_dotenv

    load_dotenv()

    handle = os.getenv("BSKY_HANDLE")
    password = os.getenv("BSKY_APP_PASSWORD")

    client = Client()
    client.login(handle, password)
    return client

def get_image_posts(client, limit=50):
    posts_with_images = []
    params = {"q": "the", "limit": limit}

    res = client.app.bsky.feed.search_posts(params=params)
    for post in res.posts:
        if post.embed and hasattr(post.embed, "images"):
            for img_view in post.embed.images:
                try:
                    url = img_view.fullsize
                    img_data = requests.get(url).content
                    img = Image.open(BytesIO(img_data))
                    post_url = f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"
                    posts_with_images.append((post_url, img))
                except Exception:
                    continue
    return posts_with_images

def get_own_image_posts(client, limit=50):
    posts_with_images = []
    feed = client.app.bsky.feed.get_timeline({'limit': limit})
    for item in feed.feed:
        post = item.post
        if hasattr(post, 'embed') and post.embed and hasattr(post.embed, 'images'):
            for img_view in post.embed.images:
                try:
                    url = img_view.fullsize
                    img_data = requests.get(url).content
                    img = Image.open(BytesIO(img_data))
                    post_url = f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"
                    posts_with_images.append((post_url, img))
                except Exception:
                    continue
    return posts_with_images
# This module handles the interaction with the Bluesky API.
# It includes functions to log in and retrieve posts with images.
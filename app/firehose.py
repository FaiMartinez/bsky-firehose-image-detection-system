import asyncio
from atproto import CAR, AtUri, models
from atproto.firehose.firehose import FirehoseSubscriber
from atproto.xrpc_client import models as xrpc_models
from PIL import Image
import requests
from io import BytesIO
import sqlite3
import json
from .hashing_utils import get_hashes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, db_path='images.db'):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_url TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    ahash TEXT NOT NULL,
                    phash TEXT NOT NULL,
                    dhash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_hashes ON images(ahash, phash, dhash)')

    async def process_post(self, post):
        try:
            if not hasattr(post, 'embed') or not post.embed or not hasattr(post.embed, 'images'):
                return

            for img in post.embed.images:
                try:
                    image_url = img.fullsize
                    response = requests.get(image_url)
                    if response.status_code != 200:
                        continue

                    image = Image.open(BytesIO(response.content)).convert('RGB')
                    hashes = get_hashes(image)
                    post_url = f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"

                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute('''
                            INSERT INTO images (post_url, image_url, ahash, phash, dhash)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            post_url,
                            image_url,
                            str(hashes['ahash']),
                            str(hashes['phash']),
                            str(hashes['dhash'])
                        ))
                        
                    logger.info(f"Processed image from post: {post_url}")
                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error processing post: {str(e)}")

class FirehoseProcessor(FirehoseSubscriber):
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()

    async def on_message_create(self, message: models.ComAtprotoSyncSubscribeRepos.RepoOp) -> None:
        if not message.record or not isinstance(message.record, models.AppBskyFeedPost.Main):
            return
        
        await self.image_processor.process_post(message.record)

async def run_firehose():
    subscriber = FirehoseProcessor()
    await subscriber.start()
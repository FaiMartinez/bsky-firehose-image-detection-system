import sqlite3
from typing import List, Dict, Tuple
import imagehash
from PIL import Image
from io import BytesIO
import requests

def search_similar_images(image: Image.Image, threshold: int = 5) -> Tuple[List[Dict], List[Dict]]:
    hashes = {
        "ahash": str(imagehash.average_hash(image)),
        "phash": str(imagehash.phash(image)),
        "dhash": str(imagehash.dhash(image))
    }
    
    with sqlite3.connect('images.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        exact_matches = []
        similar_matches = []
        
        results = cursor.execute('''
            SELECT DISTINCT post_url, image_url, ahash, phash, dhash
            FROM images
        ''').fetchall()
        
        for row in results:
            db_hashes = {
                "ahash": row['ahash'],
                "phash": row['phash'],
                "dhash": row['dhash']
            }
            
            distances = [
                abs(imagehash.hex_to_hash(hashes["ahash"]) - imagehash.hex_to_hash(db_hashes["ahash"])),
                abs(imagehash.hex_to_hash(hashes["phash"]) - imagehash.hex_to_hash(db_hashes["phash"])),
                abs(imagehash.hex_to_hash(hashes["dhash"]) - imagehash.hex_to_hash(db_hashes["dhash"]))
            ]
            
            avg_distance = sum(distances) / len(distances)
            
            result = {
                "post_url": row['post_url'],
                "image_url": row['image_url'],
                "distance": avg_distance
            }
            
            if avg_distance == 0:
                exact_matches.append(result)
            elif avg_distance <= threshold:
                similar_matches.append(result)
    
    similar_matches.sort(key=lambda x: x['distance'])
    return exact_matches, similar_matches
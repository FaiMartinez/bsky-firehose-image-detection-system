from flask import Blueprint, render_template, request, jsonify
import os
from PIL import Image
from .search_utils import search_similar_images
import asyncio
from .firehose import run_firehose
import threading

main = Blueprint('main', __name__)

def start_firehose():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_firehose())

@main.before_app_first_request
def start_firehose_crawler():
    thread = threading.Thread(target=start_firehose, daemon=True)
    thread.start()

@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            file = request.files.get("image")
            if not file:
                return jsonify({"error": "No image file provided"}), 400

            image = Image.open(file.stream).convert("RGB")
            exact_matches, similar_matches = search_similar_images(image)

            return jsonify({
                "exact_matches": exact_matches,
                "similar_matches": similar_matches
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template("index.html")

@main.route("/stats")
def stats():
    import sqlite3
    with sqlite3.connect('images.db') as conn:
        cursor = conn.cursor()
        total_images = cursor.execute('SELECT COUNT(*) FROM images').fetchone()[0]
        recent_images = cursor.execute(
            'SELECT COUNT(*) FROM images WHERE created_at > datetime("now", "-1 hour")'
        ).fetchone()[0]
    
    return jsonify({
        "total_images": total_images,
        "recent_images": recent_images
    })
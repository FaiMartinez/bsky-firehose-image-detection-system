from flask import Blueprint, render_template, request
import os
from PIL import Image
from .hashing_utils import get_hashes, compare_hashes
from .bsky_utils import login_bsky, get_own_image_posts

main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    exact_matches, similar_matches = [], []
    error = None

    if request.method == "POST":
        try:
            handle = os.getenv("BSKY_HANDLE")
            password = os.getenv("BSKY_APP_PASSWORD")
            file = request.files.get("image")

            if not handle or not password or not file:
                error = "Missing handle, password, or image file."
                return render_template("index.html", error=error)

            os.makedirs("static/uploads", exist_ok=True)
            filepath = os.path.join("static/uploads", file.filename)
            file.save(filepath)

            uploaded_img = Image.open(filepath).convert("RGB")
            uploaded_hashes = get_hashes(uploaded_img)

            client = login_bsky()
            posts = get_own_image_posts(client)

            if not posts:
                error = "No posts with images found in your recent feed."

            for post_url, img in posts:
                post_hashes = get_hashes(img.convert("RGB"))
                match_type = compare_hashes(uploaded_hashes, post_hashes)

                if match_type == "exact":
                    exact_matches.append(post_url)
                elif match_type == "similar":
                    similar_matches.append(post_url)

            os.remove(filepath)

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        exact_matches=exact_matches,
        similar_matches=similar_matches,
        error=error
    )

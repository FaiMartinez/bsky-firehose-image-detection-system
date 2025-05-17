import imagehash

def get_hashes(image):
    return {
        "ahash": imagehash.average_hash(image),
        "phash": imagehash.phash(image),
        "dhash": imagehash.dhash(image),
    }

def compare_hashes(h1, h2, threshold=5):
    distances = [
        h1["ahash"] - h2["ahash"],
        h1["phash"] - h2["phash"],
        h1["dhash"] - h2["dhash"],
    ]

    if all(d == 0 for d in distances):
        return "exact"
    elif any(d <= threshold for d in distances):
        return "similar"
    return "none"
# This module provides functions to compute and compare image hashes.
# It uses the imagehash library to generate average, perceptual, and difference hashes.
import imagehash

def get_hashes(image):
    return {
        "ahash": imagehash.average_hash(image),
        "phash": imagehash.phash(image),
        "dhash": imagehash.dhash(image),
    }

def compare_hashes(h1, h2, threshold=5):
    # Calculate Hamming distances for each hash type
    distances = [
        abs(h1["ahash"] - h2["ahash"]),
        abs(h1["phash"] - h2["phash"]),
        abs(h1["dhash"] - h2["dhash"]),
    ]
    
    # If any distance is 0, it's an exact match
    if any(d == 0 for d in distances):
        return "exact"
    # If the average distance is below threshold, it's similar
    elif sum(distances) / len(distances) <= threshold:
        return "similar"
    return "none"
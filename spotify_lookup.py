# import json
# import urllib.parse
# import requests
# import argparse

# def search_spotify(title, artist, token):
#     base = "https://api.spotify.com/v1/search"
#     query = f"{title} {artist}"
#     query_encoded = urllib.parse.quote(query)

#     url = f"{base}?q={query_encoded}&type=track&limit=1"

#     headers = {
#         "Authorization": f"Bearer {token}"
#     }

#     resp = requests.get(url, headers=headers)

#     # Token error
#     if resp.status_code == 401:
#         return {"error": "Invalid or expired token"}

#     if resp.status_code != 200:
#         return {"error": f"HTTP {resp.status_code}: {resp.text}"}

#     data = resp.json()

#     try:
#         item = data["tracks"]["items"][0]
#         return {
#             "title": item["name"],
#             "artist": ", ".join([a["name"] for a in item["artists"]]),
#             "spotify_url": item["external_urls"]["spotify"]
#         }
#     except:
#         return {"error": "No results found"}

# def lookup_all(songs, token):
#     results = []
#     for s in songs:
#         title = s["title"]
#         artist = s["artist"]
#         result = search_spotify(title, artist, token)
#         results.append(result)
#     return results

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--in", dest="infile", required=True)
#     parser.add_argument("--out", dest="outfile", required=True)
#     parser.add_argument("--token", dest="token", required=True)
#     args = parser.parse_args()

#     with open(args.infile, "r", encoding="utf-8") as f:
#         data = json.load(f)
#         songs = data["songs"]

#     results = lookup_all(songs, args.token)

#     with open(args.outfile, "w", encoding="utf-8") as f:
#         json.dump(results, f, indent=2)



# import json
# import os
# import requests
# from difflib import SequenceMatcher
# from dotenv import load_dotenv

# load_dotenv()

# SPOTIFY_ID = os.getenv("SPOTIFY_CLIENT_ID")
# SPOTIFY_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# if not SPOTIFY_ID or not SPOTIFY_SECRET:
#     raise SystemExit("❌ Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in .env")


# # -------------------------------------------------------------
# # TOKEN
# # -------------------------------------------------------------
# def get_token():
#     url = "https://accounts.spotify.com/api/token"
#     data = {"grant_type": "client_credentials"}
#     res = requests.post(url, data=data, auth=(SPOTIFY_ID, SPOTIFY_SECRET))
#     if res.status_code != 200:
#         raise RuntimeError(f"Spotify Auth Failed: {res.text}")
#     return res.json()["access_token"]


# # -------------------------------------------------------------
# # SEARCH REQUEST
# # -------------------------------------------------------------
# def spotify_search(query, token):
#     url = "https://api.spotify.com/v1/search"
#     headers = {"Authorization": f"Bearer {token}"}
#     params = {"q": query, "type": "track", "limit": 10}

#     r = requests.get(url, headers=headers, params=params)
#     if r.status_code != 200:
#         return []
#     return r.json().get("tracks", {}).get("items", [])


# # -------------------------------------------------------------
# # SIMILARITY
# # -------------------------------------------------------------
# def sim(a, b):
#     return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# # -------------------------------------------------------------
# # BEST MATCH LOGIC
# # -------------------------------------------------------------
# def best_match(input_title, input_artist, token):
#     query = f"{input_title} {input_artist}"
#     items = spotify_search(query, token)

#     if not items:
#         return {
#             "input_title": input_title,
#             "input_artist": input_artist,
#             "error": "No results"
#         }

#     best = None
#     best_score = 0.0

#     for t in items:
#         title = t["name"]
#         artist = t["artists"][0]["name"]

#         score_title = sim(input_title, title)
#         score_artist = sim(input_artist, artist)
#         score = (score_title * 0.7 + score_artist * 0.3) * 100

#         if score > best_score:
#             best_score = score
#             best = t

#     if not best:
#         return {
#             "input_title": input_title,
#             "input_artist": input_artist,
#             "error": "No good match"
#         }

#     return {
#         "input_title": input_title,
#         "input_artist": input_artist,
#         "matched_title": best["name"],
#         "matched_artist": best["artists"][0]["name"],
#         "spotify_url": best["external_urls"]["spotify"],
#         "preview_url": best.get("preview_url"),
#         "match_score": round(best_score, 2),
#     }


# # -------------------------------------------------------------
# # MAIN – READS JSON FILE AUTOMATICALLY
# # -------------------------------------------------------------
# def main():
#     INPUT_FILE = "playlist_songs.json"
#     OUTPUT_FILE = "spotify_results.json"

#     if not os.path.exists(INPUT_FILE):
#         raise SystemExit(f"❌ Input file not found: {INPUT_FILE}")

#     with open(INPUT_FILE, "r", encoding="utf-8") as f:
#         songs = json.load(f).get("songs", [])

#     token = get_token()
#     results = []

#     print("\n🎧 Searching Spotify…\n")

#     for s in songs:
#         title = s["title"]
#         artist = s["artist"]
#         print(f"→ Matching: {title}")
#         results.append(best_match(title, artist, token))

#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(results, f, indent=2)

#     print(f"\n✅ Done! Results saved to {OUTPUT_FILE}")


# if __name__ == "__main__":
#     main()


import json
import os
import requests
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not SPOTIFY_ID or not SPOTIFY_SECRET:
    raise SystemExit("❌ Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in .env")


# -------------------------------------------------------------
# TOKEN
# -------------------------------------------------------------
def get_token():
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    res = requests.post(url, data=data, auth=(SPOTIFY_ID, SPOTIFY_SECRET))
    if res.status_code != 200:
        raise RuntimeError(f"Spotify Auth Failed: {res.text}")
    return res.json()["access_token"]


# -------------------------------------------------------------
# SEARCH REQUEST
# -------------------------------------------------------------
def spotify_search(query, token):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 10}

    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        return []
    return r.json().get("tracks", {}).get("items", [])


# -------------------------------------------------------------
# SIMILARITY
# -------------------------------------------------------------
def sim(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# -------------------------------------------------------------
# BEST MATCH LOGIC
# -------------------------------------------------------------
def best_match(input_title, input_artist, token):
    query = f"{input_title} {input_artist}"
    items = spotify_search(query, token)

    if not items:
        return {
            "input_title": input_title,
            "input_artist": input_artist,
            "error": "No results"
        }

    best = None
    best_score = 0.0

    for t in items:
        title = t["name"]
        artist = t["artists"][0]["name"]

        score_title = sim(input_title, title)
        score_artist = sim(input_artist, artist)
        score = (score_title * 0.7 + score_artist * 0.3) * 100

        if score > best_score:
            best_score = score
            best = t

    if not best:
        return {
            "input_title": input_title,
            "input_artist": input_artist,
            "error": "No good match"
        }

    return {
        "input_title": input_title,
        "input_artist": input_artist,
        "matched_title": best["name"],
        "matched_artist": best["artists"][0]["name"],
        "spotify_url": best["external_urls"]["spotify"],
        "preview_url": best.get("preview_url"),
        "match_score": round(best_score, 2),
    }


# -------------------------------------------------------------
# ASK USER FOR RETENTION FLAG
# -------------------------------------------------------------
def ask_retain_old_tracks():
    """Ask user if they want to retain old tracks from previous run."""
    while True:
        response = input("\n❓ Retain old tracks from previous run? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print("   Please enter 'yes' or 'no'")


# -------------------------------------------------------------
# MAIN – READS JSON FILE AUTOMATICALLY
# -------------------------------------------------------------
def main():
    INPUT_FILE = "playlist_songs.json"
    OUTPUT_FILE = "spotify_results.json"

    if not os.path.exists(INPUT_FILE):
        raise SystemExit(f"❌ Input file not found: {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        songs = json.load(f).get("songs", [])

    # Ask user about retention
    retain_old = ask_retain_old_tracks()

    token = get_token()
    results = []

    print("\n🎧 Searching Spotify…\n")

    for s in songs:
        title = s["title"]
        artist = s["artist"]
        print(f"→ Matching: {title}")
        results.append(best_match(title, artist, token))

    # Add flag to output
    output_data = {
        "retain_old_tracks": retain_old,
        "songs": results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Done! Results saved to {OUTPUT_FILE}")
    print(f"   Retention flag: {retain_old}")


if __name__ == "__main__":
    main()
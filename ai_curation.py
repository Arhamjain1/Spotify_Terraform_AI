# import os
# import argparse
# import json
# from google import generativeai as genai

# # Load API key
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# model = genai.GenerativeModel("gemini-2.0-flash")


# def clean_json(text):
#     text = text.strip()

#     # Remove markdown fences: ```json ... ```
#     if text.startswith("```"):
#         parts = text.split("```")
#         # Typically ["", "json\n{...}", ""]
#         if len(parts) >= 2:
#             text = parts[1]  # remove outer ```
#         text = text.replace("json", "", 1).strip()

#     return text


# def get_playlist_suggestions(theme, n=20):
#     prompt = f"""
# Return ONLY valid JSON.

# Suggest EXACTLY {n} songs for the playlist theme: "{theme}".

# Output format:

# {{
#   "songs": [
#     {{"title": "Song Name", "artist": "Artist Name"}},
#     ...
#   ]
# }}
# """

#     try:
#         response = model.generate_content(prompt)
#         text = response.text.strip()

#         cleaned = clean_json(text)

#         try:
#             data = json.loads(cleaned)
#             if "songs" not in data:
#                 raise ValueError("'songs' not found in JSON")
#             return data["songs"]

#         except Exception as parse_error:
#             raise RuntimeError(f"Gemini returned invalid JSON:\n{text}")

#     except Exception as e:
#         raise RuntimeError(f"Gemini API error: {e}")


# def save_to_json(songs, output_path="playlist_songs.json"):
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump({"songs": songs}, f, indent=2)

#     print(f"\n✅ Saved song list to {output_path}")


# def main():
#     parser = argparse.ArgumentParser(description="AI song suggestion generator")
#     parser.add_argument("theme", type=str, help="Playlist theme or mood")
#     parser.add_argument("-n", type=int, default=20, help="Number of songs")
#     parser.add_argument("-o", type=str, default="playlist_songs.json", help="Output JSON file")

#     args = parser.parse_args()

#     print(f"\n🎧 Generating {args.n} songs for: '{args.theme}'...\n")

#     songs = get_playlist_suggestions(args.theme, n=args.n)

#     save_to_json(songs, args.o)


# if __name__ == "__main__":
#     main()


# import os
# import argparse
# import json
# from google import generativeai as genai

# # Load API key
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# model = genai.GenerativeModel("gemini-2.0-flash")


# def clean_json(text):
#     text = text.strip()

#     if text.startswith("```"):
#         parts = text.split("```")
#         if len(parts) >= 2:
#             text = parts[1]
#         text = text.replace("json", "", 1).strip()

#     return text


# def get_playlist_suggestions(theme, n=20):
#     # SUPER STRICT MODE PROMPT (forces real Spotify songs only)
#     prompt = f"""
# You MUST follow these rules STRICTLY:

# 1. Only suggest songs that definitely exist on Spotify.
# 2. Only use well-known, globally released tracks from verified artists.
# 3. Absolutely DO NOT create fictional songs or fictional artists.
# 4. If you are not 100% certain a song exists on Spotify, DO NOT include it.
# 5. Prefer mainstream artists (Coldplay, Weeknd, Ed Sheeran, Arijit Singh, BTS, Taylor Swift, Drake, etc.)
# 6. Avoid obscure, indie, underground, or extremely niche tracks.

# Your task:
# Suggest EXACTLY {n} songs for the playlist theme: "{theme}"

# Output ONLY valid JSON:

# {{
#   "songs": [
#     {{"title": "Song Name", "artist": "Artist Name"}}
#   ]
# }}
# """

#     try:
#         response = model.generate_content(prompt)
#         text = response.text.strip()

#         cleaned = clean_json(text)

#         try:
#             data = json.loads(cleaned)
#             if "songs" not in data:
#                 raise ValueError("'songs' not found in JSON")
#             return data["songs"]

#         except Exception:
#             raise RuntimeError(f"Gemini returned invalid JSON:\n{text}")

#     except Exception as e:
#         raise RuntimeError(f"Gemini API error: {e}")


# def save_to_json(songs, output_path="playlist_songs.json"):
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump({"songs": songs}, f, indent=2)

#     print(f"\n✅ Saved song list to {output_path}")


# def main():
#     parser = argparse.ArgumentParser(description="AI song suggestion generator")
#     parser.add_argument("theme", type=str, help="Playlist theme or mood")
#     parser.add_argument("-n", type=int, default=20, help="Number of songs")
#     parser.add_argument("-o", type=str, default="playlist_songs.json", help="Output JSON file")

#     args = parser.parse_args()

#     print(f"\n🎧 Generating {args.n} songs for: '{args.theme}'...\n")

#     songs = get_playlist_suggestions(args.theme, n=args.n)

#     save_to_json(songs, args.o)


# if __name__ == "__main__":
#     main()



import os
import argparse
import json
from google import generativeai as genai

# Load API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")


def clean_json(text):
    text = text.strip()

    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
        text = text.replace("json", "", 1).strip()

    return text


def get_playlist_suggestions(theme, n=20):
    # SUPER STRICT MODE PROMPT (forces real Spotify songs only)
    prompt = f"""
You MUST follow these rules STRICTLY:

1. Only suggest songs that definitely exist on Spotify.
2. Only use well-known, globally released tracks from verified artists.
3. Absolutely DO NOT create fictional songs or fictional artists.
4. If you are not 100% certain a song exists on Spotify, DO NOT include it.
5. Prefer mainstream artists (Coldplay, Weeknd, Ed Sheeran, Arijit Singh, BTS, Taylor Swift, Drake, etc.)
6. Avoid obscure, indie, underground, or extremely niche tracks.

Your task:
Suggest EXACTLY {n} songs for the playlist theme: "{theme}"

Output ONLY valid JSON:

{{
  "songs": [
    {{"title": "Song Name", "artist": "Artist Name"}}
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        cleaned = clean_json(text)

        try:
            data = json.loads(cleaned)
            if "songs" not in data:
                raise ValueError("'songs' not found in JSON")
            return data["songs"]

        except Exception:
            raise RuntimeError(f"Gemini returned invalid JSON:\n{text}")

    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")


def ask_retain_old_songs():
    """Ask user if they want to retain old songs from previous suggestions."""
    while True:
        response = input("\n❓ Retain old songs from previous playlist? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print("   Please enter 'yes' or 'no'")


def load_existing_songs(output_path="playlist_songs.json"):
    """Load existing songs from previous playlist if it exists."""
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("songs", [])
        except Exception as e:
            print(f"⚠️  Could not read existing songs: {e}")
            return []
    return []


def save_to_json(songs, output_path="playlist_songs.json", retain_flag=True):
    """Save songs with retention flag to JSON."""
    output_data = {
        "retain_old_songs": retain_flag,
        "songs": songs
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Saved song list to {output_path}")
    print(f"   Retention flag: {retain_flag}")


def main():
    parser = argparse.ArgumentParser(description="AI song suggestion generator")
    parser.add_argument("theme", type=str, help="Playlist theme or mood")
    parser.add_argument("-n", type=int, default=20, help="Number of songs")
    parser.add_argument("-o", type=str, default="playlist_songs.json", help="Output JSON file")

    args = parser.parse_args()

    print(f"\n🎧 Generating {args.n} songs for: '{args.theme}'...\n")

    # Ask about retention
    retain_old = ask_retain_old_songs()

    # Get new suggestions
    new_songs = get_playlist_suggestions(args.theme, n=args.n)

    # Merge with existing songs if retention is enabled
    if retain_old:
        existing_songs = load_existing_songs(args.o)
        if existing_songs:
            print(f"   Merging with {len(existing_songs)} existing songs...")
            
            # Create set of existing titles to avoid duplicates
            existing_titles = {(s["title"].lower(), s["artist"].lower()) for s in existing_songs}
            
            # Filter out duplicates from new songs
            unique_new_songs = []
            for song in new_songs:
                if (song["title"].lower(), song["artist"].lower()) not in existing_titles:
                    unique_new_songs.append(song)
            
            # Combine: new songs first, then existing
            all_songs = unique_new_songs + existing_songs
            print(f"   Final count: {len(unique_new_songs)} new + {len(existing_songs)} existing = {len(all_songs)} total")
            
            save_to_json(all_songs, args.o, retain_flag=True)
        else:
            print("   No existing songs found.")
            save_to_json(new_songs, args.o, retain_flag=True)
    else:
        print("   Skipping old songs (retention disabled)")
        save_to_json(new_songs, args.o, retain_flag=False)


if __name__ == "__main__":
    main()
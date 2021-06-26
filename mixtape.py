import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import random
import time

def main():

    cid, secret = getCreds()
    SPOTIPY_CLIENT_ID = cid
    SPOTIPY_CLIENT_SECRET = secret
    SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
    scope = "user-library-read playlist-modify-public"

    playlist_id = "4BHgp7e388zC3g7m9QA515"  # ENTER PLAYLIST ID HERE
    edit_playlist_id = "2W6gc42AFYowduiika2sHB" # ENTER PLAYLIST TO OUTPUT TO HERE - If None, will create a new playlist.

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI))

    # Get the tracks in the source playlist.
    offset = 0
    r = sp.playlist_items(playlist_id, offset=offset, fields="items(track(name, artists(id, name), id))")
    tracks = r

    # Get rest of the tracks if there's over 100 in the playlist.
    while (len(r["items"]) != 0):
        offset += len(r["items"])
        r = sp.playlist_items(playlist_id, offset=offset, fields="items(track(name, artists(id, name), id))")

        tracks["items"].extend(r["items"])
        print("Additional GET made with {0} songs returned, {1} total.".format(len(r["items"]), len(tracks["items"])))

    # Remove invalid tracks
    tracks["items"] = [x for x in tracks["items"] if validTrack(x)]


    # Obtain audio features for each track.
    track_chunks = chunks(tracks["items"], 100)
    for track_chunk in track_chunks:
        track_ids = [x["track"]["id"] for x in track_chunk]
        r = sp.audio_features(track_ids)
        for i, feature in enumerate(r):
            track_chunk[i]["track"]["audio_features"] = feature


    # Assign each song a category depending on the energy, danceability, and valence. These numbers can be tweaked to your preferences, but they're what works best for me.
    hypeTrack = []
    chillTrack = []
    for track in tracks["items"]:
        if track["track"]["audio_features"]["energy"] > 0.80 and (track["track"]["audio_features"]["danceability"] > 0.40 and track["track"]["audio_features"]["valence"] > 0.40):
            hypeTrack.append(track)
        elif track["track"]["audio_features"]["energy"] >= 0.95:
            hypeTrack.append(track)
        else:
            chillTrack.append(track)

    # Sort hype and chill tracks into high and low values based on a simple sort.
    hypeEnergy = sorted(hypeTrack, key=lambda x: x["track"]["audio_features"]["energy"])
    lowHype = hypeEnergy[:len(hypeEnergy)//2]
    highHype = hypeEnergy[len(hypeEnergy)//2:]

    chillEnergy = sorted(chillTrack, key=lambda x: x["track"]["audio_features"]["energy"])
    lowChill = chillEnergy[:len(chillEnergy)//2]
    highChill = chillEnergy[:len(chillEnergy)//2]

    #print(len(lowHype))
    #print(len(highHype))
    #print(len(lowChill))
    #print(len(highChill))

    # Shuffle each track within each subcategory.
    random.shuffle(lowHype)
    random.shuffle(highHype)
    random.shuffle(lowChill)
    random.shuffle(highChill)

    # 7 parts: chill (low energy) -> chill (high) -> hype (low) -> hype (high) -> hype (low) -> chill (high) -> chill (low)
    finalPlaylist = []
    finalPlaylist.extend(lowChill[len(lowChill)//2:])  # lowChill lower half
    finalPlaylist.extend(highChill[len(highChill)//2:])  # highChill lower half
    finalPlaylist.extend(lowHype[len(lowHype)//2:])  # lowHype lower half
    finalPlaylist.extend(highHype)  # entirety of highHipe
    finalPlaylist.extend(lowHype[:len(lowHype)//2])  # lowHyper upper half
    finalPlaylist.extend(highChill[:len(highChill)//2])  # highChill upper half
    finalPlaylist.extend(lowChill[:len(lowChill)//2])  # lowChill upper half

    finalPlaylist_ids = [x["track"]["id"] for x in finalPlaylist]

    timeStr = time.strftime("%Y.%m.%d - %H.%M.%S").strip()
    # Edit an existing playlist
    if edit_playlist_id is not None:
        for i, chunk in enumerate(chunks(finalPlaylist_ids, 100)):
            if i == 0:
                sp.playlist_replace_items(edit_playlist_id, [])
                sp.playlist_add_items(edit_playlist_id, chunk)
            else:
                sp.playlist_add_items(edit_playlist_id, chunk)

    # Make a new playlist
    else:
        r = sp.user_playlist_create(sp.current_user()["id"], "Mixtape")
        edit_playlist_id = r["id"]

        for chunk in chunks(finalPlaylist_ids, 100):
            sp.playlist_add_items(edit_playlist_id, chunk)


    # Log changes.
    with open("{0}.txt".format(timeStr), 'w', encoding="utf8") as f:
        f.write("TRACKS WRITTEN:")
        for i, track in enumerate(finalPlaylist):
            if i == 0:
                f.write("\n*****LOW CHILL (Lower Half)*****\n")
            elif i == len(lowChill)//2:
                f.write("\n*****HIGH CHILL (Lower Half)*****\n")
            elif i == (len(lowChill)//2) + (len(highChill)//2):
                f.write("\n*****LOW HYPE (Lower Half)*****\n")
            elif i == (len(lowChill)//2) + (len(highChill)//2) + (len(lowHype)//2):
                f.write("\n*****HIGH HYPE*****")
            elif i == (len(lowChill)//2) + (len(highChill)//2) + (len(lowHype)//2) + (len(highHype)):
                f.write("\n*****LOW HYPE (Upper Half)*****\n")
            elif i == (len(lowChill)//2) + (len(highChill)//2) + (len(lowHype)) + (len(highHype)):
                f.write("\n*****HIGH CHILL (Upper Half)*****\n")
            elif i == (len(lowChill)//2) + (len(highChill)) + (len(lowHype)) + (len(highHype)):
                f.write("\n*****LOW CHILL (Upper Half)*****\n")
            f.write("{0}\t {1} - {2} - ID:{3}\n".format(i, track["track"]["name"], ", ".join([x["name"] for x in track["track"]["artists"]]), track["track"]["id"]))

    # Write all our data (DEBUG PURPOSES)
    #with open("out.json", 'w', encoding="utf8") as f:
        #json.dump(tracks, f, indent=3, ensure_ascii=False)


def getCreds():
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
            return creds["client_id"], creds["secret"]
    except Exception as e:
        print("Error: {0}".format(e))


def validTrack(track):
    try:
        if track["track"]["id"] is None:
            return False
        else:
            return True
    except KeyError:
        return False


# Taken from ttps://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == "__main__":
    main()

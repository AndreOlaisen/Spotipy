import spotipy
import spotipy.util as util
import pandas as pd


def print_song(song):
    print("Song: ", song["name"])
    print("Artist: ", song["artists"][0]["name"])
    print("Album: ", song["album"]["name"])
    print("Release date: ", song["album"]["release_date"])


def print_song_uri(song_uri):
    song = sp.track(song_uri)
    print_song(song)
    
    
def get_playlist(token, playlist_uri):
    sp = spotipy.Spotify(auth=token)
    result = sp.playlist(playlist_uri, fields=None, market=None, additional_types=('track',))
    print()
    print(result['name'])
    print('  total tracks', result['tracks']['total'])
    results = sp.playlist(result['id'],
                          fields="tracks,next")
    tracks = results['tracks']
    show_tracks(tracks)
    list_of_artist_names = []
    list_of_artist_uri = []
    list_of_song_names = []
    list_of_song_uri = []
    list_of_durations_ms = []
    list_of_explicit = []
    list_of_albums = []
    list_of_album_uri = []
    list_of_album_release_date = []
    list_of_popularity = []

    while tracks['next']:
        for i, item in enumerate(tracks['items']):
            track = item['track']
            this_artists_name = track["artists"][0]["name"]
            list_of_artist_names.append(this_artists_name)
            this_artists_uri = track["artists"][0]["uri"]
            list_of_artist_uri.append(this_artists_uri)
            list_of_songs = track["name"]
            list_of_song_names.append(list_of_songs)
            song_uri = track["uri"]
            list_of_song_uri.append(song_uri)
            list_of_duration = track["duration_ms"]
            list_of_durations_ms.append(list_of_duration)
            song_explicit = track["explicit"]
            list_of_explicit.append(song_explicit)
            this_album_uri = track["album"]["uri"]
            list_of_album_uri.append(this_album_uri)
            this_album = track["album"]["name"]
            list_of_albums.append(this_album)
            release_date = track["album"]["release_date"]
            list_of_album_release_date.append(release_date)
            song_popularity = track["popularity"]
            list_of_popularity.append(song_popularity)
        tracks = sp.next(tracks)
    else:
        for i, item in enumerate(tracks['items']):
            track = item['track']
            this_artists_name = track["artists"][0]["name"]
            list_of_artist_names.append(this_artists_name)
            this_artists_uri = track["artists"][0]["uri"]
            list_of_artist_uri.append(this_artists_uri)
            list_of_songs = track["name"]
            list_of_song_names.append(list_of_songs)
            song_uri = track["uri"]
            list_of_song_uri.append(song_uri)
            list_of_duration = track["duration_ms"]
            list_of_durations_ms.append(list_of_duration)
            song_explicit = track["explicit"]
            list_of_explicit.append(song_explicit)
            this_album_uri = track["album"]["uri"]
            list_of_album_uri.append(this_album_uri)
            this_album = track["album"]["name"]
            list_of_albums.append(this_album)
            release_date = track["album"]["release_date"]
            list_of_album_release_date.append(release_date)
            song_popularity = track["popularity"]
            list_of_popularity.append(song_popularity)


    all_songs = pd.DataFrame(
        {'artist': list_of_artist_names,
         'artist_uri': list_of_artist_uri,
         'song': list_of_song_names,
         'song_uri': list_of_song_uri,
         'duration_ms': list_of_durations_ms,
         'explicit': list_of_explicit,
         'album': list_of_albums,
         'album_uri': list_of_album_uri,
         'release_date': list_of_album_release_date,
         'popularity': list_of_popularity

         })

    return all_songs


def search_for_earlier_occurrences(song_uri):
    track = sp.track(song_uri)
    track_name = track["name"].split("-")[0]
    release_date = track["album"]["release_date"]
    precision = track["album"]["release_date_precision"]
    artists_name = track["artists"][0]["name"]
    uri = track["uri"]

    # Get results based on track
    # TODO: is limit 10 really what we want? maybe less
    search_result = sp.search(track_name, limit=10, offset=0, type='track', market="NO")

    # TODO: Avoid large duration changes
    # TODO: album > compilation
    for result in search_result["tracks"]["items"]:

        res_release_date = result["album"]["release_date"]
        res_artists_name = result["artists"][0]["name"]
        res_precision = result["album"]["release_date_precision"]

        if res_precision == "day":
            if release_date > res_release_date and artists_name == res_artists_name:
                uri = result["uri"]
                release_date = res_release_date
                precision = res_precision
        else:
            if release_date.split("-")[0] > res_release_date and artists_name == res_artists_name:
                uri = result["uri"]
                release_date = res_release_date
                precision = res_precision

    return uri


def find_earlier_occurrences(known_uri, songs_uri):

    tracks = []
    change_to = []
    change = []

    for start in songs_uri:
        if start not in known_uri:
            res = search_for_earlier_occurrences(start)
            tracks.append(start)
            change_to.append(res)

            if start != res:
                print(":::::::::::::::::::\n")
                print("Change from:")
                print_song_uri(start)
                print("\nChange to:")
                print_song_uri(res)
                change.append(True)
            else:
                change.append(False)

    new_duplicate_data = pd.DataFrame({
        "track": tracks,
        "change": change,
        "wanted_track": change_to
    })

    return new_duplicate_data

# TODO: add option to not automatically do changes only suggest.
# Prefered at the same spot as the origial
def change_duplicates_playlist(token, playlist_uri, duplicates_df, user):
    sp = spotipy.Spotify(auth=token)
    playlist = get_playlist(token, playlist_uri)
    song_uri = list(playlist["song_uri"])[0:550]
    known_uri = list(duplicates_df["track"])
    new_duplicate_df = find_earlier_occurrences(known_uri, song_uri)

    all_duplicate = [duplicates_df, new_duplicate_df]
    all_duplicate = pd.concat(all_duplicate)
    all_duplicate = all_duplicate[["track", "change", "wanted_track"]]
    all_duplicate.to_csv("duplicates.csv")

    duplicates = pd.read_csv("duplicates.csv", encoding='utf-8')

    tracks_in_playlist = []
    tracks_change_to = []
    for i, uri in enumerate(list(duplicates["track"])):
        if (uri in list(song_uri)) and list(duplicates["change"])[i] == True:
            tracks_in_playlist.append(uri)
            tracks_change_to.append(duplicates["wanted_track"][i])
    print(tracks_in_playlist)
    print(tracks_change_to)

    print(len(tracks_in_playlist))
    print(len(tracks_change_to))

    sp.user_playlist_remove_all_occurrences_of_tracks(user, playlist_uri, tracks_in_playlist)
    for i in range(0, len(tracks_change_to), 100):
        sp.user_playlist_add_tracks(username, playlist_uri, tracks_change_to[i:(i + 100)])


if __name__ == "__main__":

    cid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    
    username = "XXXXXXXX"
    
    scope = 'playlist-modify-private'
    token = util.prompt_for_user_token(username,
                                       scope,
                                       client_id=cid,
                                       client_secret=secret,
                                       redirect_uri='http://localhost:8888/callback')

    sp = spotipy.Spotify(auth=token)

    duplicate_data = pd.read_csv('duplicates.csv', encoding='utf-8')
    duplicate_data = duplicate_data[["track", "change", "wanted_track"]]
    
    playlist_uri = "spotify:playlist:XXXXXXXXXXX"

    change_duplicates_playlist(token, playlist_uri, duplicate_data, username)
    """
    path = "C:/Users/User/Documents/NTNU/Annet/Spotipy/Playlists/"
    songs = pd.read_csv(path + 'alt_copy.csv', encoding='utf-8')
    song_uri = list(songs["song_uri"])
    duplicate_data = pd.read_csv('duplicates.csv', encoding='utf-8')
    known_uri = list(duplicate_data["track"])
    
    new_duplicate_df = find_earlier_occurrences(known_uri, song_uri)
    all_duplicate = [duplicate_data, new_duplicate_df]
    all_duplicate = pd.concat(all_duplicate)
    all_duplicate = all_duplicate[["track", "change", "wanted_track"]]
    all_duplicate.to_csv("duplicates.csv")
    """

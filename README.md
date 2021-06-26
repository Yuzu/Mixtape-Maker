# Mixtape Maker

Mixtape Maker is a simple Python script that will optimize your Spotify playlists using a very basic methodology that emphasizes the difference between "Hype" and "Chill" songs as determined by Spotify's Audio Features. A simple concept representing the shape of a normal distribution is applied to these classifications to create a playlist that starts off slow and chill, only to slowly ramp up to an eventual climax of hype and back down.

## Usage

Provide a valid Client ID and Secret in credentials.json, and Spotify Playlist IDs in mixtape.py, with playlist_id representing the source playlist that you want to optimize, and edit_playlist_id being the destination for the new playlist, set to None if you want to create a new playlist.

The program will output a timestamped .txt file with the new playlist as well.

## Contributing
This is a pretty simple "algorithm" that is by no means optimized mathematically/quantifiably. I merely tweaked the parameters to my liking. Recommendations would be greatly appreciated!

## Requirements
* Python
* Spotipy 2.0+

## License
[MIT](https://choosealicense.com/licenses/mit/)

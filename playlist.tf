resource "spotify_playlist" "Bollywood"{
    name="Bollywood"
    tracks=["131yybV7A3TmC34a0qE8u8"]
}

data "spotify_search_track" "Satinder_Sartaj"{
    artist="Satinder Sartaj"
}

resource "spotify_playlist" "Punjabi_Songs" {
    name="Punjabi Songs"
    tracks=[data.spotify_search_track.Satinder_Sartaj.tracks[0].id,
    data.spotify_search_track.Satinder_Sartaj.tracks[1].id]
}

resource "spotify_playlist" "happy_tracks" {
  name        = "Happy Tracks"
  description = "Uplifting songs"
  public      = false

  tracks = local.playlist_tracks
}
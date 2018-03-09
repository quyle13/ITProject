import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_project.settings')

import django
django.setup()

#-------------------------------------------------------------------------------
import requests
import random
from musicapp.models import UserProfile, Artist, Album, Song, Comment, Rating

def populate():

    # Add artists, albums and songs to the database
    searchRequest(name="ironmaiden", conn="artist")
    searchRequest(name="metallica",  conn="artist")
    searchRequest(name="megadeth",   conn="artist")
    searchRequest(name="acdc",       conn="artist")
    searchRequest(name="mastodon",   conn="artist")

    # Add rating and comment to all element
    print("Add rating and one comment to each artist")
    for a in Artist.objects.filter():
        addComment("artist", a.ArtistSlug)
        addRating( "artist", a.ArtistSlug)

    print("Add rating and one comment to each album")
    for a in Album.objects.filter():
        addComment("album", a.Artist.ArtistSlug, a.AlbumSlug)
        addRating( "album", a.Artist.ArtistSlug, a.AlbumSlug)

    print("Add rating and one comment to each song")
    for s in Song.objects.filter():
        addComment("song", s.Artist.ArtistSlug, s.Album.AlbumSlug, s.SongSlug)
        addRating( "song", s.Artist.ArtistSlug, s.Album.AlbumSlug, s.SongSlug)

def searchRequest(name="", conn="", artist="", album=""):

    if conn == "":
        searchRequest(name, conn="artist")
        searchRequest(name, conn="album")
        searchRequest(name, conn="track")

    # Send request to search information
    result = requests.get("https://api.deezer.com/search/" + conn + "?", params={'q':name})

    # Check if the HTTP response is OK
    if result.status_code == 200:
        result = result.json()

        # Don't need to populate to much
        if(result['total'] > 25):
            nbr_results = 25
        else:
            nbr_results = result['total']

        # Browse the different element in the JSON answer
        for i in range(len(result['data'])):
            data = result['data'][i]

            # If an artist field is found, search his album
            if data['type'] == "artist":

                print(data['name'], ",", data['type'])

                # Create a new artist
                artistDB                = Artist()
                artistDB.Name           = data['name']
                artistDB.PictureURL     = data['picture_medium']
                artistDB.ArtistDeezerID = data['id']

                # If the artist is not already in the DB, save it
                try:
                    artistDB = Artist.objects.get(Name=artistDB.Name)
                except Artist.DoesNotExist:
                    artistDB.save()

                # Search the albums of the artist
                searchRequest(name=data['name'], artist=data['name'], conn="album")

                # Populate the database only with the first artist found
                break;

            # If an album field is found, search his tracks
            if data['type'] == "album" and\
              (data['artist']['name'] == artist or artist == ""):

                print(artist, ",", data['title'], ",", data['type'])

                artistDB = Artist.objects.get(Name=artist)

                # Create a new album
                albumDB = Album()
                albumDB.Artist         = artistDB
                albumDB.Title          = data['title']
                albumDB.PictureURL     = data['cover_medium']
                albumDB.AlbumDeezerID  = data['id']
                albumDB.ArtistDeezerID = data['artist']['id']

                # If the album is not already in the DB, save it
                try:
                    albumDB = Album.objects.get(Title=albumDB.Title,
                                                Artist=artistDB)
                except Album.DoesNotExist:
                    albumDB.save()

                # Search the songs of the artist
                searchRequest(name=data['title'], conn="track", artist=artist,
                              album=data['title'])

                # Populate the database only with the four first albums found
                if i > 3:
                    break;

            if data['type'] == "track" and\
              (data['artist']['name'] == artist or artist == "") and\
              (data['album']['title'] == album  or album  == ""):

                print(artist, ",", album, ",", data['title'], ",", data['type'])

                artistDB = Artist.objects.get(Name=artist)
                albumDB = Album.objects.get(Title=album, Artist=artistDB)

                # Create a new song
                songDB = Song()
                songDB.Album          = albumDB
                songDB.Artist         = artistDB
                songDB.Title          = data['title']
                songDB.PictureURL     = data['album']['cover_medium']
                songDB.PreviewURL     = data['preview']
                songDB.AlbumDeezerID  = data['album']['id']
                songDB.ArtistDeezerID = data['artist']['id']
                songDB.SongDeezerID   = data['id']

                # If the song is not already in the DB, save it
                try:
                    songDB = Song.objects.get(Title=songDB.Title,
                                              Album=albumDB,
                                              Artist=artistDB)
                except Song.DoesNotExist:
                    songDB.save()

def addComment(page, artist, album="", song=""):

    com = Comment.objects.create(Username     = "populator",
                                 Content      = "populator let a comment",
                                 Artist       = artist,
                                 Album        = album,
                                 Song         = song,
                                 Comment_page = page)

    com.save()

def addRating(page, artist, album="", song=""):

    rate = Rating.objects.create(Username    = "populator",
                                 Artist      = artist,
                                 Album       = album,
                                 Song        = song,
                                 RatingValue = random.randint(0, 5),
                                 Rating_page = page)
    rate.save()

# Start execution here!
if __name__ == '__main__':
    print("Starting Musicapp opulation script...")
    populate()

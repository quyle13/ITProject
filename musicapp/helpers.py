import requests
from django.template.defaultfilters import slugify
from musicapp.models import Artist, Album, Song


def save_deezer_data_to_db(input):
    # "https://api.deezer.com/search" + "?", params = {'q': name}
    print('in call Dezzer API METHOD')

    for key, value in input.items():
        if key == 'data':
            number_of_items = len(value)

    # iterate all objects and save to data
    for i in range(number_of_items):
        each_object = input['data'][i]

        artist = Artist()
        artist.Name = each_object['artist']['name']
        artist.PictureURL = each_object['artist']['picture_medium']
        artist.ArtistDeezerID = each_object['artist']['id']
        try:
            artist.save()
        except:
            pass

        album = Album()
        album.Artist = artist
        album.Title = each_object['album']['title']
        album.PictureURL = each_object['album']['cover_medium']
        album.AlbumDeezerID = each_object['album']['id']
        album.ArtistDeezerID = each_object['artist']['id']
        try:
            album.save()
        except:
            pass

        song = Song()
        song.Album = album
        song.Artist = artist
        song.Title = each_object['title']
        song.PictureURL = each_object['album']['cover_medium']
        song.PreviewURL = each_object['preview']
        song.AlbumDeezerID = each_object['album']['id']
        song.ArtistDeezerID = each_object['artist']['id']
        song.SongDeezerID = each_object['id']
        try:
            song.save()
        except:
            pass


'''
Process search songs/albums/artist
1. User enters a keyword for searching
2. Search in local database firstly
3. If there is no information, then call Deezer API
'''


def run_query(name=""):
    returned_result = []

    # Firstly, check our database
    artist_list = Artist.objects.filter(Name__icontains=name)
    if artist_list.exists():
        print('There is Artist info in DB')
        for each_artist in artist_list:
            returned_result.append({'name': each_artist.Name,
                                    'ArtistSlug': each_artist.ArtistSlug,
                                    'PictureURL': each_artist.PictureURL,
                                    'type': 'artist'})

    song_list = Song.objects.filter(Title__icontains=name)
    if song_list.exists():
        print('There is song info in DB')
        for each_song in song_list:
            returned_result.append({'title': each_song.Title,
                                    'ArtistSlug': each_song.Artist.ArtistSlug,
                                    'AlbumSlug': each_song.Album.AlbumSlug,
                                    'SongSlug': each_song.SongSlug,
                                    'PictureURL': each_song.PictureURL,
                                    'type': 'song'})

    album_list = Album.objects.filter(Title__icontains=name)
    if album_list.exists():
        print('There is album info in DB')
        for each_album in album_list:
            returned_result.append({'title': each_album.Title,
                                    'ArtistSlug': each_song.Artist.ArtistSlug,
                                    'AlbumSlug': each_song.Album.AlbumSlug,
                                    'PictureURL': each_album.PictureURL,
                                    'type': 'album'})
    # call deezer api
    result = None
    try:
        print("Calling DEEZER API")
        result = requests.get("https://api.deezer.com/search" + "?", params={'q': name})
    except:
        print("Error when querying DEEZER API")

    # Check if the HTTP response is OK
    if result is not None and result.status_code == 200:
        temp_result = result.json()
        save_deezer_data_to_db(temp_result)
        while 'next' in temp_result.keys():
            next_link = temp_result['next']
            result = requests.get(next_link)
            temp_result = result.json()
            save_deezer_data_to_db(temp_result)
            for each_item in temp_result['data']:
                if each_item['artist']:
                    returned_result.append({'name': each_item['artist']['name'],
                                            'ArtistSlug': slugify(each_item['artist']['name']),
                                            'PictureURL': each_item['artist']['picture_medium'],
                                            'type': 'artist'})
                if each_item['album']:
                    returned_result.append({'title': each_item['album']['title'],
                                            'ArtistSlug': slugify(each_item['artist']['name']),
                                            'AlbumSlug': slugify(each_item['album']['title']),
                                            'PictureURL': each_item['album']['cover_medium'],
                                            'type': 'album'})
                returned_result.append({'title': each_item['title'],
                                        'ArtistSlug': slugify(each_item['artist']['name']),
                                        'AlbumSlug': slugify(each_item['album']['title']),
                                        'SongSlug': slugify(each_item['title']),
                                        'PictureURL': each_item['album']['cover_medium'],
                                        'type': 'song'})

        return {'returned_result': returned_result}

    '''
    This method is called when user browses to Search page.
    If Get method: return HTML page
    If POST method: call run_Query method to process
    '''

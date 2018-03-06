import requests
from django.template.defaultfilters import slugify
from musicapp.models import Artist, Album, Song
from django.db import IntegrityError
from django.contrib.sessions.backends.db import SessionStore



def save_deezer_album_songs_to_db(result, album_id, artist_id):
    for data in result['data']:
        album = Album.objects.get(AlbumDeezerID__exact=album_id)
        artist = Artist.objects.get(ArtistDeezerID__exact=artist_id)

        song = Song()
        song.Album = album
        song.Artist = artist
        song.Title = data['title']
        song.PictureURL = album.PictureURL
        song.PreviewURL = data['preview']
        song.AlbumDeezerID = album.AlbumDeezerID
        song.ArtistDeezerID = artist.ArtistDeezerID
        song.SongDeezerID = data['id']
        try:
            song = Song.objects.get(Title=song.Title)
        except Song.DoesNotExist:
            song.save()
            pass
    pass


def run_album_query(album_id, artist_id):
    result = None
    try:
        print("Calling DEEZER API")

        result = requests.get("https://api.deezer.com/album/" + str(album_id) + "/tracks")
    except:
        print("Error when querying DEEZER API")

    if result is not None and result.status_code == 200:
        temp_result = result.json()
        save_deezer_album_songs_to_db(temp_result, album_id, artist_id)

    return 1



def save_deezer_data_to_db(input):
    # "https://api.deezer.com/search" + "?", params = {'q': name}

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
            artist = Artist.objects.get(Name=artist.Name)
        except Artist.DoesNotExist:
            artist.save()
            pass

        album = Album()
        album.Artist = artist
        album.Title = each_object['album']['title']
        album.PictureURL = each_object['album']['cover_medium']
        album.AlbumDeezerID = each_object['album']['id']
        album.ArtistDeezerID = each_object['artist']['id']
        try:
            album = Album.objects.get(Title=album.Title)
        except Album.DoesNotExist:
            album.save()
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
            song = Song.objects.get(Title=song.Title)
        except Song.DoesNotExist:
            song.save()
            pass


'''
Process search songs/albums/artist
1. User enters a keyword for searching
2. Search in local database firstly
3. If there is no information, then call Deezer API
'''


def run_query(name,next_link):
    returned_result = []

    # Firstly, check our database
    artist_list = Artist.objects.filter(Name__icontains=name)
    if artist_list.exists():
        print('There is Artist info in DB')
        for each_artist in artist_list:
            returned_result.append({'name': each_artist.Name,
                                    'ArtistSlug': each_artist.ArtistSlug,
                                    'AlbumSlug': '',
                                    'SongSlug': '',
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
                                    'ArtistSlug': each_album.Artist.ArtistSlug,
                                    'AlbumSlug': each_album.AlbumSlug,
                                    'SongSlug': '',
                                    'PictureURL': each_album.PictureURL,
                                    'type': 'album'})
    # call deezer api
    result = None
    try:
        print("Calling DEEZER API")
        #check next link exists or not
        if not next_link:
            print('next link is None')
            result = requests.get("https://api.deezer.com/search" + "?", params={'q': name})
        else:

            result = requests.get(next_link)
    except:
        print("Error when querying DEEZER API")

    # Check if the HTTP response is OK
    if result is not None and result.status_code == 200:
        temp_result = result.json()
        save_deezer_data_to_db(temp_result)
        s = SessionStore()
        if 'next' in temp_result.keys():
            print("There is next link")
            next_link = temp_result['next']
            s["next_link"] = next_link
            s.save()
        else:
            del s['next_link']
            # result = requests.get(next_link)
            # temp_result = result.json()
            # save_deezer_data_to_db(temp_result)
        for each_item in temp_result['data']:
            if each_item['artist']:
                if not any(d['ArtistSlug'] == slugify(each_item['artist']['name']) for d in returned_result):
                    returned_result.append({'name': each_item['artist']['name'],
                                            'ArtistSlug': slugify(each_item['artist']['name']),
                                            'AlbumSlug': '',
                                            'SongSlug': '',
                                            'PictureURL': each_item['artist']['picture_medium'],
                                            'type': 'artist'})
            if each_item['album']:
                if not any(d['AlbumSlug'] == slugify(each_item['album']['title']) for d in returned_result):
                    returned_result.append({'title': each_item['album']['title'],
                                            'ArtistSlug': slugify(each_item['artist']['name']),
                                            'AlbumSlug': slugify(each_item['album']['title']),
                                            'SongSlug': '',
                                            'PictureURL': each_item['album']['cover_medium'],
                                            'type': 'album'})
            if not any(d['ArtistSlug'] == slugify(each_item['title']) for d in returned_result):
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

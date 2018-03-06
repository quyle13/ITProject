import xml.etree.cElementTree as ET

import requests
from django.contrib.sessions.backends.db import SessionStore
from django.template.defaultfilters import slugify

from musicapp.models import Artist, Album, Song


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
        result = requests.get("https://api.deezer.com/album/" + str(album_id) + "/tracks")
    except:
        print("Error Querying Deezer API")

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


# this is save data to data base album info related to the sepecific artist
def save_deezer_data_to_db_artist_album(input, _artist_name, _artist_deezeer_id):
    for key, value in input.items():
        if key == 'data':
            number_of_items = len(value)

    # iterate all objects and save to data
    for i in range(number_of_items):
        each_object = input['data'][i]

        album = Album()
        album.Artist = _artist_name
        album.Title = each_object['title']
        album.PictureURL = each_object['cover_medium']
        album.AlbumDeezerID = each_object['id']
        album.ArtistDeezerID = _artist_deezeer_id
        try:
            album = Album.objects.get(Title=album.Title)
        except Album.DoesNotExist:
            album.save()

            pass


'''
Process search songs/albums/artist
1. User enters a keyword for searching
2. Search in local database firstly
3. If there is no information, then call Deezer API
'''
def run_query(name, next_link):
    returned_result = []

    # Firstly, check our database
    artist_list = Artist.objects.filter(Name__icontains=name)
    if artist_list.exists():
        for each_artist in artist_list:
            returned_result.append({'name': each_artist.Name,
                                    'ArtistSlug': each_artist.ArtistSlug,
                                    'AlbumSlug': '',
                                    'SongSlug': '',
                                    'PictureURL': each_artist.PictureURL,
                                    'type': 'artist'})

    song_list = Song.objects.filter(Title__icontains=name)
    if song_list.exists():
        for each_song in song_list:
            returned_result.append({'title': each_song.Title,
                                    'ArtistSlug': each_song.Artist.ArtistSlug,
                                    'AlbumSlug': each_song.Album.AlbumSlug,
                                    'SongSlug': each_song.SongSlug,
                                    'PictureURL': each_song.PictureURL,
                                    'type': 'song'})

    album_list = Album.objects.filter(Title__icontains=name)
    if album_list.exists():
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
        # check next link exists or not
        if not next_link:
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


def run_query_artist(_artist_name):
    # query for related album
    # Firstly, check our database
    returned_result = []
    album_list = Album.objects.filter(Artist__Name__icontains=_artist_name)
    if album_list.exists():
        for each_album in album_list:
            returned_result.append({'title': each_album.Title,
                                    'ArtistSlug': each_album.Artist.ArtistSlug,
                                    'AlbumSlug': each_album.AlbumSlug,
                                    'SongSlug': '',
                                    'PictureURL': each_album.PictureURL,
                                    'type': 'album'})
    # call deezer api
    singer_name = Artist.objects.get(ArtistSlug=_artist_name)
    artist_deezeer_id = str(singer_name.ArtistDeezerID)
    result = requests.get("https://api.deezer.com/artist/" + artist_deezeer_id + "/albums")

    # Check if the HTTP response is OK
    if result is not None:
        temp_result = result.json()
        save_deezer_data_to_db_artist_album(temp_result, singer_name, artist_deezeer_id)
        if 'next' in temp_result.keys():  # if the result has "next"
            next_link = temp_result['next']
            result = requests.get(next_link)
            temp_result = result.json()
            save_deezer_data_to_db_artist_album(temp_result, singer_name, artist_deezeer_id)
            for each_item in temp_result['data']:
                if not any(d['AlbumSlug'] == slugify(each_item['title']) for d in returned_result):
                    returned_result.append({'title': each_item['title'],
                                            'ArtistSlug': slugify(_artist_name),
                                            'AlbumSlug': slugify(each_item['title']),
                                            'SongSlug': '',
                                            'PictureURL': each_item['cover_medium'],
                                            'type': 'album'})

        else:  # With the result has not "next"

            for each_item in temp_result['data']:
                if not any(d['AlbumSlug'] == slugify(each_item['title']) for d in returned_result):
                    returned_result.append({'title': each_item['title'],
                                            'ArtistSlug': slugify(_artist_name),
                                            'AlbumSlug': slugify(each_item['title']),
                                            'SongSlug': '',
                                            'PictureURL': each_item['cover_medium'],
                                            'type': 'album'})
    return returned_result


def detail_artist(_artist_name):
    singer_name = Artist.objects.get(ArtistSlug=_artist_name)
    artist_deezeer_id = str(singer_name.ArtistDeezerID)
    detail = requests.get("https://api.deezer.com/artist/" + artist_deezeer_id)
    detail_dic = detail.json()

    return detail_dic['nb_album'], detail_dic['nb_fan']


def detail_song(_song_name, _artist_name):
    song_name = Song.objects.get(SongSlug=_song_name)
    song_deezeer_id = str(song_name.SongDeezerID)
    detail = requests.get("https://api.deezer.com/track/" + song_deezeer_id)
    detail_dic = detail.json()

    replace_name = str(_artist_name)
    replace_name = replace_name.replace('-', '%20')
    replace_song_name = str(_song_name)
    replace_song_name = replace_song_name.replace('-', '%20')

    lyric = requests.get("http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist=" +
                         replace_name + "&song=" + replace_song_name)

    root = ET.fromstring(lyric.content)
    for child in root.iter('{http://api.chartlyrics.com/}Lyric'):
        print(child.text)
        lyric_text = child.text

    detail_dic['lyric'] = lyric_text

    return detail_dic['rank'], detail_dic['release_date'], detail_dic['lyric']

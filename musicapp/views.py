from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout
from musicapp.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from musicapp.forms import UserForm, UserEditForm
from django.core.files.storage import FileSystemStorage
from musicapp.forms import UserForm
from musicapp.models import Artist, Album, Song
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import requests


def index(request):
    context_dict = dict()
    context_dict['page_title'] = 'Music App Homepage'
    return render(request, 'musicapp/index.html', context=context_dict)


def contact(request):
    context_dict = dict()
    context_dict['page_title'] = 'Contact Us'
    return render(request, 'musicapp/contact.html', context=context_dict)


def about(request):
    context_dict = dict()
    context_dict['page_title'] = 'About Us'
    return render(request, 'musicapp/about.html', context=context_dict)


def register(request):
    context_dict = dict()
    context_dict['page_title'] = 'Register for Music App'
    context_dict['register_active'] = True

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        context_dict['user_form'] = user_form
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            auth_login(request, user)
            return HttpResponseRedirect(reverse('home'))
        else:
            print(user_form.errors)

    else:
        user_form = UserForm()
    return render(request, 'musicapp/register.html', context=context_dict)


def login(request):
    context_dict = dict()
    context_dict['page_title'] = 'Login to Music App'
    context_dict['login_active'] = True
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect(reverse('home'))
            else:
                context_dict['error_msg'] = "Your account is disabled."
                return render(request, 'musicapp/login.html', context=context_dict)
        else:
            context_dict['error_msg'] = "Username and password does not match "
    return render(request, 'musicapp/login.html', context=context_dict)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required
def profile(request):
    context_dict = dict()
    context_dict['page_title'] = 'My Profile'
    context_dict['user'] = request.user
    context_dict['playlists'] = None
    context_dict['playlist_songs'] = None

    if request.method == 'POST':
        user_edit_form = UserEditForm(user=request.user, data=request.POST)
        context_dict['user_edit_form'] = user_edit_form
        if user_edit_form.is_valid():
            if user_edit_form.cleaned_data.get('password') != '':
                u = User.objects.get(username__exact=request.user.username)
                u.set_password(user_edit_form.cleaned_data.get('password'))
                u.save()
                context_dict['notification_success'] = True
                context_dict['notification_message'] = 'Password Successfully Changed'
            if request.FILES.get('profile_picture'):
                profile_picture = request.FILES.get('profile_picture')
                fs = FileSystemStorage()
                filename = profile_picture.name
                file, ext = filename.split('.')
                file = request.user.username
                filename = file + '.' + ext
                filename = fs.save(filename, profile_picture)
                uploaded_file_url = fs.url(filename)
                try:
                    u = UserProfile.objects.get(user_id=request.user.id)
                    u.profile_picture = uploaded_file_url
                    u.save()
                except UserProfile.DoesNotExist:
                    u = UserProfile(user_id=request.user.id, profile_picture=uploaded_file_url)
                    u.save()
                context_dict['notification_success'] = True
                context_dict['notification_message'] = 'Profile Picture Updated'
            if user_edit_form.cleaned_data.get('password') == '' and request.FILES.get('profile_picture') is None:
                context_dict['notification_warning'] = True
                context_dict['notification_message'] = 'No change made to your profile'
        else:
            print(user_edit_form.errors)

    else:
        user_edit_form = UserEditForm(user=request.user)
    return render(request, 'musicapp/profile.html', context=context_dict)


def playlist(request, playlist_name):
    context_dict = dict()
    context_dict['page_title'] = 'My Playlist'
    return render(request, 'musicapp/playlist.html', context=context_dict)

def callDezzerAPI(temp_result, returned_result):
    # "https://api.deezer.com/search" + "?", params = {'q': name}
    print ('in call Dezzer API METHOD')

    for key, value in temp_result.items():
        if key == 'data':
            number_of_items = len(value)

    # iterate all objects and save to data
    for i in range(number_of_items):
        each_object = temp_result['data'][i]

        if each_object['type'] == 'artist':
            artist = Artist()
            artist.Name = each_object['name']
            artist.PictureURL = each_object['picture_medium']
            artist.NumberAlbum = each_object['nb_album']
            artist.ArtistDeezerID = each_object['id']
            artist.save()

        # #processing for Songs/Albums
        elif each_object['type'] == 'album':
            album = Album()
            album.Title = each_object['title']
            album.PictureURL = each_object['cover_medium']
            album.NumberOfTracks = each_object['nb_tracks']
            album.URL = each_object['link']
            album.AlbumDeezerID = each_object['id']
            album.ArtistDeezerID = each_object['artist']['id']
            album.save()
        else:
            song = Song()
            song.Title = each_object['title_short']
            song.URL = each_object['link']
            song.PictureURL = each_object['album']['cover_medium']
            song.AlbumDeezerID = each_object['album']['id']
            song.ArtistDeezerID = each_object['artist']['id']
            song.SongDeezerID = each_object['id']
            song.save()



'''
Process search songs/albums/artist
1. User enters a keyword for searching
2. Search in local database firstly
3. If there is no information, then call Deezer API
'''
def run_Query(name=""):
    returned_result = []
    #Firstly, check our database
    artist_list = Artist.objects.filter(Name__icontains=name)
    if artist_list.exists():
        print ('Artist - There is information in DB')
        for each_artist in artist_list:
            returned_result.append({'name': each_artist.Name,'PictureURL': each_artist.PictureURL,'type':'artist'})
    # If we don't find any thing in our database, then send request to search information
    print ("name=",name)
    tracks = Song.objects.filter(Title__icontains=name)
    # tracks = Song.objects.all()
    print ("Total track:", len(tracks))
    if tracks.exists():
        print ('Track - There is information in DB')
        for each_track in tracks:
            returned_result.append({'title': each_track.Title, 'Link': each_track.URL,'type':'track','PictureURL':each_track.PictureURL})

    album_list = Album.objects.filter(Title__icontains=name)
    if album_list.exists():
        print ('Album - There is information in DB')
        for each_album in album_list:
            returned_result.append({'title': each_album.Title, 'PictureURL': each_album.PictureURL,
                                    'NumberOfTracks': each_album.NumberOfTracks,'type':'album'})
    # not have information in database
    if not returned_result:

        try:
            print("Calling DEEZER API")
            result = requests.get("https://api.deezer.com/search"  + "?", params={'q':name})
        except:
            print("Error when querying DEEZER API")

        # Check if the HTTP response is OK

        if result.status_code == 200:
            temp_result = result.json()
            callDezzerAPI(temp_result, returned_result)
            while ('next' in temp_result.keys()):
                next_link = temp_result['next']
                result = requests.get(next_link)
                temp_result = result.json()
                callDezzerAPI(temp_result, returned_result)
                for each_item in temp_result['data']:
                    if each_item['type'] == 'artist':
                        returned_result.append({'name': each_artist['name'],
                                                'PictureURL': each_artist['picture_medium'], 'type': 'artist'})
                    elif each_item['type'] == 'track':
                        returned_result.append({'title': each_item['title_short'],
                                                'URL': each_item['link'], 'type': 'track',
                                                'PictureURL': each_item['album']['cover_medium']})
                    else:
                        returned_result.append({'title': each_item['title'],
                                                'PictureURL': each_item['PictureURL'],
                                                'NumberOfTracks': each_item['NumberOfTracks']
                                                   , 'type': 'album'
                                                })



    return {'returned_result':returned_result}

'''
This method is called when user browses to Search page.
If Get method: return HTML page
If POST method: call run_Query method to process
'''
def search(request):
    context_dict = dict()
    context_dict['page_title'] = 'Search for Songs, Albums, Artists'
    page = request.GET.get('page')
    #Clear all previous data for the first running
    if page is None:
        if 'keyword' in request.session:
            del request.session['keyword']
        if 'returned_list' in request.session:
            del request.session['returned_list']

    print ('IN GET MODE')
    keyword = request.GET.get('searchValue')
    #TODO:Ask Tutor about how to get submited value when user navigate beween pages
    #Temporarily process
    if keyword is None and page is not None:
         keyword = request.session.get('keyword')
    print (keyword)
    if keyword is not None:
        if 'returned_list' in request.session:
            returned_list = request.session.get('returned_list')
        else:
            returned_list = run_Query(name=keyword)
            request.session['returned_list'] = returned_list

        paginator = Paginator(returned_list['returned_result'], 25)
        # show the search value when user submits the form
        context_dict["keyword"] = keyword
        request.session['keyword'] = keyword
        try:
            context_dict["returned_list"] = paginator.page(page)
        except PageNotAnInteger:
            context_dict["returned_list"] = paginator.page(1)
        except EmptyPage:
            context_dict["returned_list"] = paginator.page(paginator.num_pages)

    return render(request, 'musicapp/search.html', context=context_dict)


def artist(request, artist_name):
    context_dict = dict()
    context_dict['page_title'] = artist_name
    return render(request, 'musicapp/artist.html', context=context_dict)


def album(request, artist_name, album_name):
    context_dict = dict()
    context_dict['page_title'] = album_name + ' by: ' + artist_name
    return render(request, 'musicapp/album.html', context=context_dict)


def song(request, artist_name, album_name, song_title):
    context_dict = dict()
    context_dict['page_title'] = song_title + ' by: ' + artist_name + ' on: ' + album_name
    return render(request, 'musicapp/song.html', context=context_dict)

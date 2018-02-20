from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout
from musicapp.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from musicapp.forms import UserForm, UserEditForm
from django.core.files.storage import FileSystemStorage

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
        request.user.userprofile.profile_picture
        user_edit_form = UserEditForm(user=request.user, data=request.POST)
        context_dict['user_edit_form'] = user_edit_form
        if user_edit_form.is_valid():
            if user_edit_form.cleaned_data.get('password') != '':
                u = UserProfile.objects.get(username__exact=request.user.username)
                u.set_password(user_edit_form.cleaned_data.get('password'))
                u.save()
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
        else:
            print(user_edit_form.errors)

    else:
        user_edit_form = UserEditForm(user=request.user)
    return render(request, 'musicapp/profile.html', context=context_dict)


def playlist(request, playlist_name):
    context_dict = dict()
    context_dict['page_title'] = 'My Playlist'
    return render(request, 'musicapp/playlist.html', context=context_dict)


def search(request):
    context_dict = dict()
    context_dict['page_title'] = 'Search for Songs, Albums, Artists'

    def searchRequest(name="", conn="", artist="", album=""):

        if conn == "":
            searchRequest(name, conn="artist")
            searchRequest(name, conn="album")
            searchRequest(name, conn="track")

        # Send request to search information
        result = requests.get("https://api.deezer.com/search/" + conn + "?", params={'q': name})

        # Check if the HTTP response is OK
        if result.status_code == 200:
            result = result.json()

            # Browse the different element in the JSON answer
            for i in range(result['total']):
                data = result['data'][i]

                # If an artist field is found, search his album
                if data['type'] == "artist":
                    print(data['name'], data['type'])
                    searchRequest(name=data['name'], artist=data['name'], conn="album")

                # If an album field is found, search his tracks
                if data['type'] == "album" and \
                        (data['artist']['name'] == artist or artist == ""):
                    print(data['title'], data['type'])
                    searchRequest(name=data['title'], conn="track", artist=artist, album=data['title'])

                if data['type'] == "track" and \
                        (data['artist']['name'] == artist or artist == "") and \
                        (data['album']['title'] == album or album == ""):
                    print(data['title'], data['type'])

    # Just for example
    searchRequest(name="Mastodon", conn="artist")

    # Get the API: https://developers.deezer.com/

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

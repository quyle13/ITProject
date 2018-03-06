from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout
from musicapp.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from musicapp.forms import UserForm, CommentForm, RatingForm, PlaylistForm
from .models import *
from django.db.models import Avg
from musicapp.forms import UserForm, UserEditForm
from django.core.files.storage import FileSystemStorage
from musicapp.models import Artist, Album, Song
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from musicapp.helpers import *
import re
import requests



def index(request):
    context_dict = dict()
    context_dict['page_title'] = 'Music App Homepage'

    # Get the songs ordred regarding the rate
    topSongs_list = []
    for rate in Rating.objects.order_by('-RatingValue').filter(Rating_page='song')[:5]:
        topSongs_list.extend(Song.objects.filter(SongSlug=rate.Song))

    # Get the albums ordred regarding the rate
    topAlbums_list = []
    for rate in Rating.objects.order_by('-RatingValue').filter(Rating_page='album')[:5]:
        topAlbums_list.extend(Album.objects.filter(AlbumSlug=rate.Album))

    # Get the artists ordred regarding the rate
    topArtistes_list = []
    for rate in Rating.objects.order_by('-RatingValue').filter(Rating_page='artist')[:5]:
        topArtistes_list.extend(Artist.objects.filter(ArtistSlug=rate.Artist))

    context_dict['top_songs']    = topSongs_list
    # context_dict['new_songs']    = newSongs_list
    context_dict['top_albums']   = topAlbums_list
    # context_dict['new_albums']   = newAlbums_list
    context_dict['top_artists']  = topArtistes_list
    # context_dict['top_artists'] = newArtistes_list

    return render(request, 'musicapp/index.html', context=context_dict)


def contact(request):
    context_dict = dict()
    context_dict['page_title'] = 'Contact Us'
    context_dict['contact_active'] = True
    return render(request, 'musicapp/contact.html', context=context_dict)


def about(request):
    context_dict = dict()
    context_dict['page_title'] = 'About Us'
    context_dict['about_active'] = True
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
    context_dict['playlists'] = PlayList.objects.filter(UserID=request.user)
    context_dict['playlist_songs'] = Song.objects.filter(playlist__in=context_dict['playlists']).distinct()

    if request.method == 'POST':
        user_edit_form = UserEditForm(user=request.user, data=request.POST)
        add_playlist_form = PlaylistForm(data=request.POST)

        context_dict['user_edit_form'] = user_edit_form
        context_dict['add_playlist_form'] = add_playlist_form

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
        elif add_playlist_form.is_valid():
            p = PlayList()
            p.UserID = request.user
            p.Name = add_playlist_form.cleaned_data.get('playlist_name')
            p.save()
            context_dict['notification_success'] = True
            context_dict['notification_message'] = 'New playlist added'
        else:
            print(user_edit_form.errors)
            print(add_playlist_form.errors)

    else:
        user_edit_form = UserEditForm(user=request.user)
        add_playlist_form = PlaylistForm()
    return render(request, 'musicapp/profile.html', context=context_dict)


def playlist(request, playlist_name):
    context_dict = dict()
    context_dict['playlists'] = PlayList.objects.filter(UserID=request.user)
    context_dict['playlist'] = PlayList.objects.get(PlayListSlug=playlist_name, UserID=request.user)
    context_dict['page_title'] = context_dict['playlist'].Name
    context_dict['playlist_songs'] = Song.objects.filter(playlist=context_dict['playlist']).distinct()
    return render(request, 'musicapp/playlist.html', context=context_dict)


def search(request):
    context_dict = dict()
    context_dict['page_title'] = 'Search for Songs, Albums, Artists'
    context_dict['search_active'] = True

    page = request.GET.get('page')
    print(page)
    # Clear all previous data for the first running
    if page is None:
        if 'keyword' in request.session:
            del request.session['keyword']
        if 'returned_list' in request.session:
            del request.session['returned_list']

    keyword = request.GET.get('searchValue')
    print(keyword)
    # TODO:Ask Tutor about how to get submited value when user navigate beween pages
    # Temporarily process
    if keyword is None and page is not None:
        keyword = request.session.get('keyword')
    if keyword is not None:
        if 'returned_list' in request.session:
            returned_list = request.session.get('returned_list')
        else:
            returned_list = run_query(name=keyword)
            request.session['returned_list'] = returned_list

        paginator = Paginator(returned_list['returned_result'], 24)
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


def song(request, artist_name, album_name, song_name):
    context_dict = dict()
    context_dict['page_title'] = song_name + ' by: ' + artist_name + ' on: ' + album_name
    context_dict['song_active'] = True
    context_dict['comment_form'] = CommentForm({'author': request.user.username,
                                                'artist': artist_name,
                                                'album': album_name,
                                                'song': song_name,
                                                'comment_page': 'song'})

    context_dict['rating_form'] = RatingForm({'author': request.user.username,
                                              'artist': artist_name,
                                              'album': album_name,
                                              'song': song_name,
                                              'rating_page': 'song'})

    context_dict['detail'] = detail_song(song_name, artist_name)
    print(context_dict['detail'])


    try:
        rates = Rating.objects.filter(Artist=artist_name,
                                      Album=album_name,
                                      Song=song_name).order_by('id')
        avg_rates = rates.aggregate(Avg('RatingValue'))

        if avg_rates['RatingValue__avg'] is not None:
            context_dict['avg_int'] = int(avg_rates['RatingValue__avg'])

        comments = Comment.objects.filter(Artist=artist_name,
                                          Album=album_name,
                                          Song=song_name).order_by('-id')[:10]
        comment_list = []
        for com in comments:
            comment_list.append(com)

        context_dict['comment_list'] = comment_list

    except Exception as e:
        print(e)

    context_dict['song'] = Song.objects.get(SongSlug=song_name)

    return render(request, 'musicapp/song.html', context=context_dict)


def artist(request, artist_name):
    context_dict = dict()
    context_dict['page_title'] = artist_name
    context_dict['artist_active'] = True
    context_dict['comment_form'] = CommentForm({'author': request.user.username,
                                               'artist': artist_name,
                                                'comment_page': 'artist'})

    context_dict['rating_form'] = RatingForm({'author': request.user.username,
                                             'artist': artist_name,
                                              'rating_page': 'artist'})

    context_dict['detail'] = detail_artist(artist_name)
    context_dict['returned_list'] = run_query_artist(artist_name)
    print("this is context")
    print(context_dict)

    try:
        rates = Rating.objects.filter(Artist=artist_name,
                                      Album='',
                                      Song='').order_by('id')
        avg_rates = rates.aggregate(Avg('RatingValue'))

        if avg_rates['RatingValue__avg'] is not None:
            context_dict['avg_int'] = int(avg_rates['RatingValue__avg'])

        comments = Comment.objects.filter(Artist=artist_name,
                                          Album='',
                                          Song='').order_by('-id')[:10]
        comment_list = []
        for com in comments:
            comment_list.append(com)

        context_dict['comment_list'] = comment_list
    except Exception as e:
        print(e)

    context_dict['artist'] = Artist.objects.get(ArtistSlug=artist_name)

    return render(request, 'musicapp/artist.html', context=context_dict)


def album(request, artist_name, album_name):
    context_dict = dict()
    context_dict['page_title'] = artist_name + ' on: ' + album_name
    context_dict['album_active'] = True
    context_dict['comment_form'] = CommentForm({'author': request.user.username,
                                                'artist': artist_name,
                                                'album': album_name,
                                                'comment_page': 'album'})

    context_dict['rating_form'] = RatingForm({'author': request.user.username,
                                              'artist': artist_name,
                                              'album': album_name,
                                              'rating_page': 'album'})
    try:
        rates = Rating.objects.filter(Artist=artist_name,
                                      Album=album_name,
                                      Song='').order_by('id')
        avg_rates = rates.aggregate(Avg('RatingValue'))

        if avg_rates['RatingValue__avg'] is not None:
            context_dict['avg_int'] = int(avg_rates['RatingValue__avg'])

        comments = Comment.objects.filter(Artist=artist_name, Album=album_name, Song='').order_by('-id')[:10]
        comment_list = []
        for com in comments:
            comment_list.append(com)

        context_dict['comment_list'] = comment_list

    except Exception as e:
        print(e)

    context_dict['album'] = Album.objects.get(AlbumSlug=album_name, Artist__ArtistSlug=artist_name)


    if request.user.is_authenticated:
        context_dict['playlists'] = PlayList.objects.filter(UserID=request.user)

    return render(request, 'musicapp/album.html', context=context_dict)


def comment_post(request):
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            com = Comment.objects.create(Username=comment_form.cleaned_data["author"],
                                         Content=comment_form.cleaned_data["comment"],
                                         Artist=comment_form.cleaned_data["artist"],
                                         Album=comment_form.cleaned_data["album"],
                                         Song=comment_form.cleaned_data["song"],
                                         Comment_page=comment_form.cleaned_data["comment_page"])
            com.save()

        else:
            return HttpResponse("Submit failed")
    if com.Comment_page == 'artist':
        return HttpResponseRedirect('/view' + '/' + com.Comment_page + '/' + com.Artist + '/' + com.Album)
    else:
        return HttpResponseRedirect(
            '/view' + '/' + com.Comment_page + '/' + com.Artist + '/' + com.Album + '/' + com.Song)


def rating_post(request):
    if request.method == 'POST':
        rating_form = RatingForm(data=request.POST)
        if rating_form.is_valid():
            rate = Rating.objects.create(Username=rating_form.cleaned_data["author"],
                                         Artist=rating_form.cleaned_data["artist"],
                                         Album=rating_form.cleaned_data["album"],
                                         Song=rating_form.cleaned_data["song"],
                                         RatingValue=rating_form.cleaned_data["value"],
                                         Rating_page=rating_form.cleaned_data["rating_page"])
            rate.save()

        else:
            return HttpResponse("Rating failed")

    if rate.Rating_page == 'artist':
        return HttpResponseRedirect('/view' + '/' + rate.Rating_page + '/' + rate.Artist + '/' + rate.Album)
    else:
        return HttpResponseRedirect(
            '/view' + '/' + rate.Rating_page + '/' + rate.Artist + '/' + rate.Album + '/' + rate.Song)
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from musicapp.forms import UserForm, CommentForm, RatingForm
from .models import *
from django.db.models import Avg


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


def profile(request, profile_id):
    context_dict = dict()
    context_dict['page_title'] = 'My Profile'
    return render(request, 'musicapp/profile.html', context=context_dict)


def playlist(request, playlist_name):
    context_dict = dict()
    context_dict['page_title'] = 'My Playlist'
    return render(request, 'musicapp/playlist.html', context=context_dict)


def search(request):
    context_dict = dict()
    context_dict['page_title'] = 'Search for Songs, Albums, Artists'
    return render(request, 'musicapp/search.html', context=context_dict)


def song(request, artist_name, album_name, song_title):

    comment_form = CommentForm({'author': request.user.username,
                                'artist': artist_name,
                                'album': album_name,
                                'song': song_title,
                                'comment_page': 'song'})

    rating_form = RatingForm({'author': request.user.username,
                              'artist': artist_name,
                              'album': album_name,
                              'song': song_title,
                              'rating_page': 'song'})
    try:
        rates = Rating.objects.filter(Artist=artist_name,
                                      Album=album_name,
                                      Song=song_title).order_by('-id')[:10]
        avg_rates = rates.aggregate(Avg('RatingValue'))

        if avg_rates['RatingValue__avg'] is not None:
            avg_int = int(avg_rates['RatingValue__avg'])

        comments = Comment.objects.filter(Artist=artist_name,
                                          Album=album_name,
                                          Song=song_title).order_by('-id')[:10]
        comment_list = []
        for com in comments:
            comment_list.append(com)
    except Exception as e:
        print(e)
    return render(request, 'musicapp/song.html', locals())


def artist(request, artist_name):
    comment_form = CommentForm({'author': request.user.username,
                                'artist': artist_name,
                                'comment_page': 'artist'})

    rating_form = RatingForm({'author': request.user.username,
                              'artist': artist_name,
                              'rating_page': 'artist'})

    try:
        rates = Rating.objects.filter(Artist=artist_name,
                                      Album='',
                                      Song='').order_by('-id')[:10]
        avg_rates = rates.aggregate(Avg('RatingValue'))

        if avg_rates['RatingValue__avg'] is not None:
            avg_int = int(avg_rates['RatingValue__avg'])

        comments = Comment.objects.filter(Artist=artist_name,
                                          Album='',
                                          Song='').order_by('-id')[:10]
        comment_list = []
        for com in comments:
            comment_list.append(com)
    except Exception as e:
        print(e)
    return render(request, 'musicapp/artist.html', locals())


def album(request, artist_name, album_name):

    comment_form = CommentForm({'author': request.user.username,
                                'artist': artist_name,
                                'album': album_name,
                                'comment_page': 'album'})

    rating_form = RatingForm({'author': request.user.username,
                              'artist': artist_name,
                              'album': album_name,
                              'rating_page': 'album'})

    try:
        rates = Rating.objects.filter(Artist=artist_name,
                                      Album=album_name,
                                      Song='').order_by('-id')[:10]
        avg_rates = rates.aggregate(Avg('RatingValue'))

        if avg_rates['RatingValue__avg'] is not None:
            avg_int = int(avg_rates['RatingValue__avg'])

        comments = Comment.objects.filter(Artist=artist_name, Album=album_name, Song='').order_by('-id')[:10]
        comment_list = []
        for com in comments:
            comment_list.append(com)
    except Exception as e:
        print(e)

    return render(request, 'musicapp/album.html', locals())


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
        return HttpResponseRedirect('/view' + '/' + com.Comment_page + '/' + com.Artist + '/' + com.Album + '/' + com.Song)


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
        return HttpResponseRedirect('/view' + '/' + rate.Rating_page + '/' + rate.Artist + '/' + rate.Album + '/' + rate.Song)




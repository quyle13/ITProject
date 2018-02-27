from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout
from musicapp.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from musicapp.forms import UserForm, CommentForm, RatingForm
from .models import *
from django.db.models import Avg
from musicapp.forms import UserForm, UserEditForm
from django.core.files.storage import FileSystemStorage
from musicapp.models import Artist, Album, Song
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from musicapp.helpers import *
import requests



def index(request):
    context_dict = dict()
    context_dict['page_title'] = 'Music App Homepage'
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


def search(request):
    context_dict = dict()
    context_dict['page_title'] = 'Search for Songs, Albums, Artists'
    context_dict['search_active'] = True

    page = request.GET.get('page')
    # Clear all previous data for the first running
    if page is None:
        if 'keyword' in request.session:
            del request.session['keyword']
        if 'returned_list' in request.session:
            del request.session['returned_list']

    keyword = request.GET.get('searchValue')
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

def song(request, artist_name, album_name, song_title):
    context_dict = dict()
    context_dict['page_title'] = song_title + ' by: ' + artist_name + ' on: ' + album_name
    return render(request, 'musicapp/song.html', context=context_dict)


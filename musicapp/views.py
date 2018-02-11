from django.shortcuts import render


def index(request):
    context_dict = dict()
    context_dict['page_title'] = 'Music App Homepage'
    return render(request, 'musicapp/index.html', context=context_dict)


def register(request):
    context_dict = dict()
    context_dict['page_title'] = 'Register for Music App'
    context_dict['register_active'] = True
    return render(request, 'musicapp/register.html', context=context_dict)


def login(request):
    context_dict = dict()
    context_dict['page_title'] = 'Login to Music App'
    context_dict['login_active'] = True
    return render(request, 'musicapp/login.html', context=context_dict)


def profile(request, profile_id):
    context_dict = dict()
    context_dict['page_title'] = 'My Profile'
    return render(request, 'musicapp/profile.html', context=context_dict)


def search(request):
    context_dict = dict()
    context_dict['page_title'] = 'Search for Songs, Albums, Artists'
    return render(request, 'musicapp/search.html', context=context_dict)


def album(request, artist_name, album_name):
    context_dict = dict()
    context_dict['page_title'] = album_name + ' by: ' + artist_name
    return render(request, 'musicapp/album.html', context=context_dict)

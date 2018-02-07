from django.shortcuts import render


def index(request):
    context_dict = {}
    return render(request, 'musicapp/index.html', context=context_dict)


def register(request):
    context_dict = {}
    return render(request, 'musicapp/register.html', context=context_dict)


def login(request):
    context_dict = {}
    return render(request, 'musicapp/login.html', context=context_dict)

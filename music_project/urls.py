"""music_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

from music_project import settings
from musicapp import ajax_views
from musicapp import views

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^register/$', views.register, name='register'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^search/$', views.search, name='search'),
    url(r'^view/artist/(?P<artist_name>[\w\-]+)/$', views.artist, name='artist'),
    url(r'^view/album/(?P<artist_name>[\w\-]+)/(?P<album_name>[\w\-]+)/$', views.album, name='album'),
    url(r'^view/song/(?P<artist_name>[\w\-]+)/(?P<album_name>[\w\-]+)/(?P<song_name>[\w\-]+)/$',
        views.song, name='song'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^playlist/(?P<playlist_name>[\w\-]+)/$', views.playlist, name='playlist'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^components/new_comment/$', views.comment_post, name='comment_post'),
    url(r'^components/rate_modal/$', views.rating_post, name='rating_post'),
    # url(r'^test/$', views.test, name='test')

    # internal ajax views
    url(r'^ajax/add-to-playlist/(?P<ids>[\w\-]+)$', ajax_views.add_to_playlist),
    url(r'^next-song/$', views.next_song, name='next-song'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

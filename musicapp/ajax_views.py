from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from musicapp.models import PlayList, Song

# file used for internal processing of any ajax requests

@login_required
def add_to_playlist(request, ids):
    playlist_id, song_id = ids.split('-')
    song = Song.objects.get(pk=song_id)
    playlist = PlayList.objects.get(pk=playlist_id)
    playlist.Songs.add(song)
    return HttpResponse('Success')

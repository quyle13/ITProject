from django.contrib import admin
from musicapp.models import Genre,Artist,Song,Comment,Rating,Album,PlayList

# Register your models here.
admin.site.register(Genre)
admin.site.register(Artist)
admin.site.register(Comment)
admin.site.register(Song)
admin.site.register(Rating)
admin.site.register(Album)
admin.site.register(PlayList)
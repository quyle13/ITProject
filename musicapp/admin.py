from django.contrib import admin

from musicapp.models import *

# Register your models here.
admin.site.register(Artist)
admin.site.register(Comment)
admin.site.register(Song)
admin.site.register(Rating)
admin.site.register(Album)
admin.site.register(PlayList)

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    profile_picture = models.ImageField(null=True, upload_to='profile_pictures/')

class Genre(models.Model):
    Name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return "%s the genre" % self.name


class Artist(models.Model):
    Name = models.CharField(max_length=400, unique=True)
    Featuring = models.CharField(max_length=400)
    isBand = models.BooleanField(default=False)
    Member = models.CharField(max_length=4000)
    Rating = models.FloatField(default=0)
    Comment = models.TextField(None)
    PersonalWebsite = models.CharField(max_length=400)
    PictureURL = models.URLField(default="")
    NumberAlbum = models.IntegerField(default=0)
    #ID from Deezer
    ArtistDeezerID = models.IntegerField(default=0)
    def __str__(self):
        return "Artist Name %s " % self.Name


class Song(models.Model):
    Title = models.CharField(max_length=200)
    ArtistName = models.CharField(max_length=400,default="")
    URL = models.URLField()
    # ReleasedDate = models.DateField(default=None)
    # Genre = models.OneToOneField(Genre,on_delete = models.CASCADE,
    #                              primary_key=True)
    Rating = models.FloatField(default=0)
    Comment = models.TextField(default="")
    PictureURL = models.URLField(default="")
    ArtistDeezerID =  models.IntegerField(default=0)
    SongDeezerID = models.IntegerField(default=0)
    AlbumDeezerID = models.IntegerField(default=0)

    def __str__(self):
        return "%s is the song" % self.Title


class Comment(models.Model):
    Content = models.CharField(max_length=40000)
    RatingType = models.CharField(max_length=128)
    ItemID = models.IntegerField()
    RatingDate = models.DateField()

    def __str__(self):
        return "%s is content of comment" % self.Content


class Rating(models.Model):
    ItemID = models.IntegerField()
    RatingType = models.CharField(max_length=128)
    UserID = models.IntegerField()
    RatingDate = models.DateField()
    RatingValue = models.FloatField(default=0)

    def __str__(self):
        return "Rating Type %s , Rating Value %s" % self.RatingType % self.RatingValue


class Album(models.Model):
    Title = models.CharField(max_length=400)
    Artist = models.OneToOneField(Artist, models.CASCADE)
    URL = models.URLField()
    UploadDate = models.DateField()
    ReleasedDate = models.DateField()
    Genre = models.OneToOneField(Genre, on_delete=models.CASCADE)
    Rating = models.FloatField(default=0)
    Comment = models.TextField(None)
    Song = models.ForeignKey(Song)
    PictureURL = models.URLField(default="")
    NumberOfTracks = models.IntegerField(default=1)

    ArtistDeezerID = models.IntegerField(default=0)
    AlbumDeezerID = models.IntegerField(default=0)

    def __str__(self):
        return "Album Name %s " % Title


class PlayList(models.Model):
    PlayListName = models.CharField(max_length=400)
    UserID = models.IntegerField()
    Song = models.ForeignKey(Song)
    CreatedDate = models.DateField()

    def __str__(self):
        return "Play List Name %s " % PlayListName

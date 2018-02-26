from django.db import models
from django import forms
# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField()


class Genre(models.Model):
    Name = models.CharField(max_length=128, unique=True)
    
    def __str__(self):
        return "%s the genre" % self.Name


class Artist(models.Model):
    Name = models.CharField(max_length=400, unique=True)
    Featuring = models.CharField(max_length=400)
    isBand = models.BooleanField(default=False)
    Member = models.CharField(max_length=4000)
    Rating = models.FloatField()
    Comment = models.TextField(None)
    PersonalWebsite = models.CharField(max_length=400)

    def __str__(self):
        return "Artist Name %s " % self.Name


class Song(models.Model):
    Title = models.CharField(max_length=200)
    Artist = models.ForeignKey(Artist)
    URL = models.URLField()
    ReleasedDate = models.DateField()
    Genre = models.OneToOneField(Genre, on_delete=models.CASCADE,
                                 primary_key=True)
    Rating = models.FloatField(default=0)
    Comment = models.TextField(default="")

    def __str__(self):
        return "%s is the song" % self.Title


class Comment(models.Model):
    Username = models.CharField(max_length=50)
    Content = models.TextField(max_length=1000)
    Artist = models.CharField(max_length=400)
    Album = models.CharField(max_length=400)
    Song = models.CharField(max_length=200)
    Comment_page = models.CharField(max_length=400)

    def __str__(self):
        return "%s is content of comment" % self.Content


class Rating(models.Model):
    Username = models.CharField(max_length=50)
    Artist = models.CharField(max_length=400)
    Album = models.CharField(max_length=400)
    Song = models.CharField(max_length=200)
    RatingValue = models.IntegerField()
    Rating_page = models.CharField(max_length=400)

    def __str__(self):
        return "Rating Value %s" % self.RatingValue


class Album(models.Model):
    ItemID = models.IntegerField(unique=True, default=0)
    Title = models.CharField(max_length=400)
    Artist = models.OneToOneField(Artist, models.CASCADE)
    URL = models.URLField()
    UploadDate = models.DateField()
    ReleasedDate = models.DateField()
    Genre = models.OneToOneField(Genre, on_delete=models.CASCADE)
    Rating = models.FloatField(default=0)
    Comment = models.TextField(None)
    Song = models.ForeignKey(Song)

    def __str__(self):
        return "Album Name %s " % self.Title


class PlayList(models.Model):
    PlayListName = models.CharField(max_length=400)
    UserID = models.IntegerField()
    Song = models.ForeignKey(Song)
    CreatedDate = models.DateField()

    def __str__(self):
        return "Play List Name %s " % self.PlayListName


from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    profile_picture = models.ImageField(null=True, upload_to='profile_pictures/')


class Artist(models.Model):
    ArtistSlug = models.SlugField()
    Name = models.CharField(max_length=400, unique=True)
    Featuring = models.CharField(max_length=400)
    isBand = models.BooleanField(default=False)
    Member = models.CharField(max_length=4000)
    Rating = models.FloatField(default=0)
    Comment = models.TextField(None)
    PersonalWebsite = models.CharField(max_length=400)
    PictureURL = models.URLField(default="")
    ArtistDeezerID = models.IntegerField(default=0)

    def __str__(self):
        return "%s " % self.Name

    def save(self):
        self.ArtistSlug = slugify(self.Name)
        super(Artist, self).save()


class Album(models.Model):
    AlbumSlug = models.SlugField()
    Title = models.CharField(max_length=400)
    Artist = models.OneToOneField(Artist, models.CASCADE)
    UploadDate = models.DateField(null=True)
    ReleasedDate = models.DateField(null=True)
    Rating = models.FloatField(default=0)
    Comment = models.TextField(default="")
    PictureURL = models.URLField(default="")
    NumberOfTracks = models.IntegerField(default=1)
    ArtistDeezerID = models.IntegerField(default=0)
    AlbumDeezerID = models.IntegerField(default=0)

    def __str__(self):
        return "%s" % self.Title

    def save(self):
        self.AlbumSlug = slugify(self.Title)
        super(Album, self).save()


class Song(models.Model):
    SongSlug = models.SlugField()
    Title = models.CharField(max_length=200)
    Album = models.OneToOneField(Album, models.CASCADE)
    Artist = models.OneToOneField(Artist, models.CASCADE)
    Rating = models.FloatField(default=0)
    Comment = models.TextField(default="")
    PictureURL = models.URLField(default="")
    PreviewURL = models.URLField(default="")
    SongDeezerID = models.IntegerField(default=0)
    ArtistDeezerID = models.IntegerField(default=0)
    AlbumDeezerID = models.IntegerField(default=0)

    def __str__(self):
        return "%s" % self.Title

    def save(self):
        self.SongSlug = slugify(self.Title)
        super(Song, self).save()


class Comment(models.Model):
    Content = models.CharField(max_length=40000)
    RatingType = models.CharField(max_length=128)
    ItemID = models.IntegerField()
    RatingDate = models.DateField()

    def __str__(self):
        return "%s" % self.Content


class Rating(models.Model):
    ItemID = models.IntegerField()
    RatingType = models.CharField(max_length=128)
    UserID = models.IntegerField()
    RatingDate = models.DateField()
    RatingValue = models.FloatField(default=0)

    def __str__(self):
        return "%s - %s" % self.RatingType % self.RatingValue


class PlayList(models.Model):
    PlayListName = models.CharField(max_length=400)
    UserID = models.ForeignKey(User)
    Songs = models.ManyToManyField(Song)
    CreatedDate = models.DateField()

    def __str__(self):
        return "%s" % self.PlayListName

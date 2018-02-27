from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AlbumSlug', models.SlugField()),
                ('Title', models.CharField(max_length=400)),
                ('UploadDate', models.DateField(null=True)),
                ('ReleasedDate', models.DateField(null=True)),
                ('Rating', models.FloatField(default=0)),
                ('Comment', models.TextField(default='')),
                ('PictureURL', models.URLField(default='')),
                ('NumberOfTracks', models.IntegerField(default=1)),
                ('ArtistDeezerID', models.IntegerField(default=0)),
                ('AlbumDeezerID', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ArtistSlug', models.SlugField()),
                ('Name', models.CharField(max_length=400, unique=True)),
                ('Featuring', models.CharField(max_length=400)),
                ('isBand', models.BooleanField(default=False)),
                ('Member', models.CharField(max_length=4000)),
                ('Rating', models.FloatField(default=0)),
                ('Comment', models.TextField()),
                ('PersonalWebsite', models.CharField(max_length=400)),
                ('PictureURL', models.URLField(default='')),
                ('ArtistDeezerID', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ItemID', models.IntegerField(default=0, unique=True)),
                ('Title', models.CharField(max_length=400)),
                ('URL', models.URLField()),
                ('UploadDate', models.DateField()),
                ('ReleasedDate', models.DateField()),
                ('Rating', models.FloatField(default=0)),
                ('Comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=400, unique=True)),
                ('Featuring', models.CharField(max_length=400)),
                ('isBand', models.BooleanField(default=False)),
                ('Member', models.CharField(max_length=4000)),
                ('Rating', models.FloatField()),
                ('Comment', models.TextField()),
                ('PersonalWebsite', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='PlayList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PlayListName', models.CharField(max_length=400)),
                ('CreatedDate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ItemID', models.IntegerField()),
                ('RatingType', models.CharField(max_length=128)),
                ('UserID', models.IntegerField()),
                ('RatingDate', models.DateField()),
                ('RatingValue', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', models.ImageField(null=True, upload_to='profile_pictures/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(

            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SongSlug', models.SlugField()),
                ('Title', models.CharField(max_length=200)),
                ('Rating', models.FloatField(default=0)),
                ('Comment', models.TextField(default='')),
                ('PictureURL', models.URLField(default='')),
                ('PreviewURL', models.URLField(default='')),
                ('SongDeezerID', models.IntegerField(default=0)),
                ('ArtistDeezerID', models.IntegerField(default=0)),
                ('AlbumDeezerID', models.IntegerField(default=0)),
                ('Album', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='musicapp.Album')),
                ('Artist', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='musicapp.Artist')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', models.ImageField(null=True, upload_to='profile_pictures/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='playlist',
            name='Songs',
            field=models.ManyToManyField(to='musicapp.Song'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='UserID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='album',
            name='Artist',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='musicapp.Artist'),
        ),
    ]

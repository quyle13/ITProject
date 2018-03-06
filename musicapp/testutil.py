"""
This util class is used for testing


"""
from musicapp.models import  User, UserProfile,Artist
def create_user():
    # Create a user
    user = User.objects.get_or_create(username="testuser", password="test1234",
                                      first_name="Test", last_name="User", email="testuser@testuser.com")[0]
    user.set_password(user.password)
    user.save()

    return user

def create_artist():
    artist = Artist()
    artist.Name = 'Celine Dion'
    artist.PersonalWebsite = 'http://www.testartist.com'
    artist.ArtistDeezerID = 100
    artist.ArtistSlug ='Celine-Dion'
    artist.save()
    return artist

def create_song():
    song = Song()
    song.Title = "Because you loved me"
    song.SongSlug = "Because-you-loved-me"
    song.save()
    return song
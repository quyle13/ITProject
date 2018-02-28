from django import forms
from django.contrib.auth.models import User
from musicapp.models import PlayList


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match ")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_count = User.objects.filter(email=email).count()
        if email_count:
            raise forms.ValidationError('Email already exists')
        return email


class CommentForm(forms.Form):
    author = forms.CharField(widget=forms.HiddenInput())
    comment = forms.CharField(widget=forms.HiddenInput())
    artist = forms.CharField(widget=forms.HiddenInput(), required=False)
    album = forms.CharField(widget=forms.HiddenInput(), required=False)
    song = forms.CharField(widget=forms.HiddenInput(), required=False)
    comment_page = forms.CharField(widget=forms.HiddenInput(), required=False)


class RatingForm(forms.Form):
    author = forms.CharField(widget=forms.HiddenInput(), required=False)
    value = forms.IntegerField(widget=forms.HiddenInput())
    artist = forms.CharField(widget=forms.HiddenInput(), required=False)
    album = forms.CharField(widget=forms.HiddenInput, required=False)
    song = forms.CharField(widget=forms.HiddenInput, required=False)
    rating_page = forms.CharField(widget=forms.HiddenInput(), required=False)


class UserEditForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('password', 'confirm_password', 'profile_picture')

    def __init__(self, user, data=None):
        self.user = user
        super(UserEditForm, self).__init__(data=data)

    def clean_current_password(self):
        password = self.cleaned_data.get('current_password', None)
        if not self.user.check_password(password):
            raise forms.ValidationError("Password is incorrect")

    def clean(self):
        cleaned_data = super(UserEditForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


class PlaylistForm(forms.ModelForm):
    playlist_name = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = PlayList
        fields = ('playlist_name',)

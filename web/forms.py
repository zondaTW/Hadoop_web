from django import forms
from .models import Post
from PIL import Image

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text',)

class UploadForm(forms.Form):
    username=forms.CharField()
    uploadfile=forms.FileField()

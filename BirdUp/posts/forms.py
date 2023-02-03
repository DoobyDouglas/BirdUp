from .models import Post, Comment, Group
from django import forms
from django.forms import ModelForm


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class GroupForm(ModelForm):

    class Meta:
        model = Group
        fields = ('title', 'slug', 'description')


class SearchForm(forms.Form):
    query = forms.CharField(max_length=200)

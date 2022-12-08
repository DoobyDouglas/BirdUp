from .models import Post, Comment, Group
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

from django.shortcuts import get_object_or_404
from .models import Post, Group, Follow
from posts.forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


User = get_user_model()

# Количество постов на странице
POSTS_ON_PAGE = 10


# Главная
class Index(ListView):
    template_name = 'posts/index.html'
    model = Post
    paginate_by = POSTS_ON_PAGE

    def get_context_data(self, **kwargs):
        context = {
            'index': True,
        }
        return super().get_context_data(**context)


# Профиль
class Profile(ListView):
    template_name = 'posts/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        return Post.objects.filter(author__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user.is_authenticated:
            following = Follow.objects.filter(
                user=user, author=author
            ).exists()
        else:
            following = False
        if user != author:
            follow_button = True
        else:
            follow_button = False
        context = {
            'author': author,
            'following': following,
            'follow_button': follow_button,
        }
        return super().get_context_data(**context)


# Пост
class PostDetail(DetailView):
    template_name = 'posts/post_detail.html'
    model = Post
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form = CommentForm()
        author = post.author
        count = author.posts.count()
        comments = post.comments.all()
        context = {
            'post': post,
            'count': count,
            'form': form,
            'comments': comments,
        }
        return super().get_context_data(**context)


# Группа
class GroupPosts(ListView):
    template_name = 'posts/group_list.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        return Post.objects.filter(group__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        post_list = group.group_posts.all()
        count = post_list.count()
        context = {
            'group': group,
            'count': count,
        }
        return super().get_context_data(**context)


# Создание поста
class PostCreate(CreateView, LoginRequiredMixin):
    template_name = 'posts/create_post.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = {
            'is_edit': False,
        }
        return super().get_context_data(**context)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse(
            'posts:profile',
            kwargs={'username': self.object.author.username}
        )


# Редактирование поста
class PostEdit(UpdateView, LoginRequiredMixin):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form = PostForm(instance=post)
        context = {
            'form': form,
            'is_edit': True,
            'post': post,
        }
        return super().get_context_data(**context)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if post.author != request.user:
            return redirect('posts:post_detail',
                            post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


# Комментарии к посту
class AddComment(CreateView, LoginRequiredMixin):
    template_name = 'posts/post_comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        user = get_object_or_404(User, id=self.request.user.id)
        comment = form.save(commit=False)
        comment.author = user
        comment.post = post
        comment.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Cтраница ленты
class FollowIndex(ListView, LoginRequiredMixin):
    template_name = 'posts/follow.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = {
            'follow': True,
        }
        return super().get_context_data(**context)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Подписка
class ProfileFollow(View, LoginRequiredMixin):

    def get(self, request, username):
        user = request.user
        author = get_object_or_404(User, username=username)
        follow = Follow.objects.filter(user=user, author=author)
        if user != author and not follow.exists():
            Follow.objects.create(user=user, author=author)
        return redirect('posts:profile', username=author.username)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Отписка
class ProfileUnfollow(View, LoginRequiredMixin):

    def get(self, request, username):
        user = request.user
        author = get_object_or_404(User, username=username)
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
        return redirect('posts:profile', username=author.username)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

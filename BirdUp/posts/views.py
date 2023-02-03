from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Group, Follow
from posts.forms import PostForm, CommentForm, GroupForm, SearchForm
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic import View
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
        return Post.objects.filter(
            author__username=self.kwargs['username']).filter(
                group__isnull=True
        )

    def get_context_data(self, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, username=self.kwargs['username'])
        no_group = Post.objects.filter(
            author__username=self.kwargs['username']).filter(
                group__isnull=True
        )
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
            'profile': True,
            'no_group': no_group,
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
    slug_url_kwarg = 'slug'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        return Post.objects.filter(group__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        user = self.request.user
        post_list = group.group_posts.all()
        count = post_list.count()
        if group.creator == self.request.user:
            group_post = True
        elif self.request.user.is_authenticated:
            group_post = Follow.objects.filter(user=user, group=group).exists()
        else:
            group_post = False
        if self.request.user.is_authenticated:
            following = Follow.objects.filter(
                user=user, group=group
            ).exists()
        else:
            following = False
        context = {
            'group': group,
            'count': count,
            'following': following,
            'group_post': group_post,
            'group_list': True,
        }
        return super().get_context_data(**context)


# Создание поста
class PostCreate(CreateView, LoginRequiredMixin):
    template_name = 'posts/create_post.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        groups = Group.objects.filter(
            group_following__user=self.request.user
        )
        context = {
            'is_edit': False,
            'groups': groups,
        }
        return super().get_context_data(**context)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        if post.group in Group.objects.all():
            return redirect('posts:group_list', slug=post.group.slug)
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
        post_group = get_object_or_404(Post, id=self.kwargs['post_id'])
        post = form.save(commit=False)
        post.group = post_group.group
        post.save()
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
        author_following = Post.objects.filter(
            author__following__user=self.request.user
        )
        group_following = Post.objects.filter(
            group__group_following__user=self.request.user
        )
        return list(author_following | group_following)

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


# Создание группы
class GroupCreate(CreateView, LoginRequiredMixin):
    template_name = 'posts/create_group.html'
    form_class = GroupForm

    def form_valid(self, form):
        group = form.save(commit=False)
        group.creator = self.request.user
        group.save()
        Follow.objects.create(user=self.request.user, group=group)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Список групп
class GroupIndex(ListView):
    template_name = 'posts/groups.html'
    model = Group
    paginate_by = POSTS_ON_PAGE

    def get_context_data(self, **kwargs):
        context = {
            'groups': True,
        }
        return super().get_context_data(**context)


# Подписка на группу
class GroupFollow(View, LoginRequiredMixin):

    def get(self, request, slug):
        user = request.user
        group = get_object_or_404(Group, slug=slug)
        follow = Follow.objects.filter(user=user, group=group)
        if not follow.exists():
            Follow.objects.create(user=user, group=group)
        return redirect('posts:group_list', slug=slug)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Отписка от группы
class GroupUnfollow(View, LoginRequiredMixin):

    def get(self, request, slug):
        user = request.user
        group = get_object_or_404(Group, slug=slug)
        follow = Follow.objects.filter(user=user, group=group)
        if follow.exists():
            follow.delete()
        return redirect('posts:group_list', slug=slug)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Создание поста в группе
class GroupPostCreate(CreateView, LoginRequiredMixin):
    template_name = 'posts/group_post.html'
    form_class = PostForm
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        context = {
            'group': group,
        }
        return super().get_context_data(**context)

    def form_valid(self, form):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        post = form.save(commit=False)
        post.author = self.request.user
        post.group = group
        post.save()
        if post.group in Group.objects.all():
            return redirect('posts:group_list', slug=post.group.slug)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        follow = Follow.objects.filter(user=user, group=group)
        if not follow.exists() and group.creator != self.request.user:
            return redirect('posts:group_list',
                            slug=self.kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)


# Поиск по постам
class PostSearchView(ListView):
    model = Post
    template_name = 'posts/post_search.html'
    paginate_by = POSTS_ON_PAGE

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        form = SearchForm()
        if query == '':
            return redirect('posts:index')
        elif query:
            self.object_list = self.get_queryset()
        return render(
            request,
            self.template_name,
            {'form': form, 'page_obj': self.object_list, 'query': query}
        )

    def get_queryset(self):
        query = self.request.GET.get('query')
        return Post.objects.filter(text__icontains=query)


# Поиск по пользователям
class UserSearchView(ListView):
    model = User
    template_name = 'posts/user_search.html'
    paginate_by = POSTS_ON_PAGE

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        form = SearchForm()
        if query == '':
            return redirect('posts:index')
        elif query:
            self.object_list = self.get_queryset()
        return render(
            request,
            self.template_name,
            {'form': form, 'page_obj': self.object_list, 'query': query}
        )

    def get_queryset(self):
        query = self.request.GET.get('query')
        first_name = User.objects.filter(first_name__icontains=query)
        last_name = User.objects.filter(last_name__icontains=query)
        username = User.objects.filter(username__icontains=query)
        return list(first_name | last_name | username)


# Поиск по группам
class GroupSearchView(ListView):
    model = Group
    template_name = 'posts/group_search.html'
    paginate_by = POSTS_ON_PAGE

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        form = SearchForm()
        if query == '':
            return redirect('posts:index')
        elif query:
            self.object_list = self.get_queryset()
        return render(
            request,
            self.template_name,
            {'form': form, 'page_obj': self.object_list, 'query': query}
        )

    def get_queryset(self):
        query = self.request.GET.get('query')
        title = Group.objects.filter(title__icontains=query)
        description = Group.objects.filter(description__icontains=query)
        return list(title | description)


# Подписчики группы
class GroupFollowers(ListView):
    template_name = 'posts/group_followers.html'
    slug_url_kwarg = 'slug'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return User.objects.filter(follower__group=group)

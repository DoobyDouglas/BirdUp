import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from ..models import Group, Post, Follow
from users.models import Profile
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='HasNoName')
        cls.profile = Profile.objects.create(user=cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, тестовый пост, тестовый пост',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': 'test-slug'
                }): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={
                    'username': f'{self.user.username}'
                }): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': f'{self.post.id}'
                }): 'posts/post_detail.html',
            reverse('posts:create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': f'{self.post.id}'
                }): 'posts/create_post.html',

        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый пост, '
                         'тестовый пост, тестовый пост')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_posts_page_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['group']
        second_object = response.context['page_obj'][0]
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        post_text_0 = second_object.text
        post_image_0 = second_object.image
        self.assertEqual(group_title_0, 'Тестовая группа')
        self.assertEqual(group_slug_0, 'test-slug')
        self.assertEqual(post_text_0, 'Тестовый пост, '
                         'тестовый пост, тестовый пост')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_profile_page_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'})
        )
        first_object = response.context['page_obj'][0]
        second_object = response.context['author']
        post_text_0 = first_object.text
        post_author_0 = second_object.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый пост, '
                         'тестовый пост, тестовый пост')
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_detail_page_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'})
        )
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый пост, '
                         'тестовый пост, тестовый пост')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_create_page_correct_context(self):
        response = self.authorized_client.get(reverse('posts:create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.profile = Profile.objects.create(user=cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост, тестовый пост, тестовый пост {i}',
                author=cls.user,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': 'test-slug'
                }),
            reverse(
                'posts:profile',
                kwargs={
                    'username': f'{self.user.username}'
                }),
        )
        for address in urls:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        urls = (
            reverse('posts:index') + '?page=2',
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': 'test-slug'
                }) + '?page=2',
            reverse(
                'posts:profile',
                kwargs={
                    'username': f'{self.user.username}'
                }) + '?page=2',
        )
        for address in urls:
            response = self.client.get(address)
            self.assertEqual(len(response.context['page_obj']), 3)


# class CacheTest(TestCase):
    # @classmethod
    # def setUpClass(cls):
        # super().setUpClass()
        # cls.user = User.objects.create_user(username='HasNoName')
        # cls.group = Group.objects.create(
            # title='Тестовая группа',
            # slug='test-slug',
            # description='Тестовое описание',
        # )
        # cls.post = Post.objects.create(
            # author=cls.user,
            # text='Тестовый пост, тестовый пост, тестовый пост',
            # group=cls.group,
        # )

    # def setUp(self):
        # self.guest_client = Client()

    # def test_cache_index(self):
        # response_1 = self.guest_client.get(reverse('posts:index'))
        # post_0 = self.post
        # post_0.delete()
        # response_2 = self.guest_client.get(reverse('posts:index'))
        # self.assertEqual(response_1.content, response_2.content)
        # cache.clear()
        # response_3 = self.guest_client.get(reverse('posts:index'))
        # self.assertNotEqual(response_1.content, response_3.content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_following = User.objects.create_user(username='following')
        cls.profile = Profile.objects.create(user=cls.user_following)
        cls.user_follower = User.objects.create_user(username='follower')
        cls.profile = Profile.objects.create(user=cls.user_follower)
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тестовый пост для ленты',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_following = Client()
        self.authorized_follower = Client()
        self.authorized_following.force_login(self.user_following)
        self.authorized_follower.force_login(self.user_follower)

    def test_follow(self):
        response = self.authorized_follower.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': f'{self.user_following.username}'
                    })
        )
        self.assertEqual(Follow.objects.all().count(), 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username': f'{self.user_following.username}'
            })
        )
        response = self.guest_client.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': f'{self.user_following.username}'
                    })
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next='
            f'/profile/{self.user_following.username}/follow/')

    def test_unfollow(self):
        self.authorized_follower.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': f'{self.user_following.username}'
                    })
        )
        response = self.authorized_follower.get(
            reverse('posts:profile_unfollow',
                    kwargs={
                        'username': f'{self.user_following.username}'
                    })
        )
        self.assertEqual(Follow.objects.all().count(), 0)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username': f'{self.user_following.username}'
            })
        )

    def test_feed(self):
        self.authorized_follower.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': f'{self.user_following.username}'
                    })
        )
        response = self.authorized_follower.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост для ленты')
        response = self.authorized_following.get(reverse('posts:follow_index'))
        self.assertNotContains(response, 'Тестовый пост для ленты')

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Post, Group
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, тестовый пост, тестовый пост'
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/nopagehere/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        response = self.guest_client.get('/nopagehere/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_for_all(self):
        urls = (
            '/',
            '/group/test-slug/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/',
        )
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_edit_guest(self):
        urls = (
            '/create/',
            f'/posts/{self.post.id}/edit/',
        )
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_authorized(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_author(self):
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_authorized(self):
        self.user = User.objects.create_user(username='HasNoNameNu')
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

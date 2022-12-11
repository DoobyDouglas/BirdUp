import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from ..models import Group, Post, Comment
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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
            text='Тестовый пост, тестовый пост, тестовый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст',
            image='posts/small.gif',
        ).exists())
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:group_list',
                              kwargs={'slug': f'{self.group.slug}'}))
        response = self.guest_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit(self):
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': f'{self.post.id}'
                    }), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': f'{self.post.id}'}))
        self.assertTrue(Post.objects.filter(text='Тестовый текст 2').exists())
        response = self.guest_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': f'{self.post.id}'
                    }), data=form_data, follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )
        self.user = User.objects.create_user(username='HasNoName2')
        self.authorized_client.force_login(self.user)
        form_data = {
            'text': 'Тестовый текст 3',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': f'{self.post.id}'
                    }), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': f'{self.post.id}'}))
        self.assertFalse(Post.objects.filter(text='Тестовый текст 3').exists())

    def test_comment_post(self):
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={
                        'post_id': f'{self.post.id}'
                    }), data={'text': 'Тестовый комментарий'}, follow=True
        )
        first_object = response.context['comments'][0]
        comment_text_0 = first_object.text
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': f'{self.post.id}'}))
        self.assertTrue(
            Comment.objects.filter(text='Тестовый комментарий').exists()
        )
        self.assertEqual(comment_text_0, 'Тестовый комментарий')

        response = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={
                        'post_id': f'{self.post.id}'
                    }), data={'text': 'Тестовый комментарий 2'}, follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')
        self.assertFalse(
            Comment.objects.filter(text='Тестовый комментарий 2').exists()
        )

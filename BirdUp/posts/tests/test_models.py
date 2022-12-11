from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
            creator=cls.user,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, тестовый пост, тестовый пост'
        )

    def test_models_have_correct_object_names(self):
        expected_object_name = self.post.text[:15]
        self.assertEqual(expected_object_name, str(self.post))
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))

    def test_verbose_name(self):
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)

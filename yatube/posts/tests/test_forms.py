from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_post(self):
        """При отправке валидной формы создаётся новая запись."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.latest('id')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_edit_post(self):
        """При отправке валидной формы происходит изменение поста."""
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        changed_post = Post.objects.get(id=self.post.id)
        self.assertEqual(changed_post.text, form_data['text'])
        self.assertEqual(changed_post.group.id, form_data['group'])

    def test_guest_can_not_create_new_post(self):
        """Неавторизованный клиент перенаправляется на страницу
        авторизации"""
        posts_count = Post.objects.count()
        response = self.client.post(
            reverse('posts:post_create'),
            follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(posts_count, Post.objects.count())

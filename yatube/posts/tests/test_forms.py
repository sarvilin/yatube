import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm
from ..models import Group, Post, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Тестовый коммент',
            post=cls.post
        )
        cls.form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_post(self):
        """При отправке валидной формы создаётся новая запись."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'image': self.post.image,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': self.author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                group=form_data['group'],
                text=form_data['text'],
                image=form_data['image'],
            ).exists()
        )

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

    def test_only_authorized_user_can_leave_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Text comment',
        }
        response = self.authorized_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        last_comment = Comment.objects.latest('created')
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.author, self.author)

        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_added_comment_is_on_post_detail_page(self):
        response = self.authorized_author.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertIn(self.comment, response.context['comments'])

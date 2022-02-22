from linecache import cache

from django.contrib.auth import get_user_model
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Comment
from ..views import NUM_OF_POST

User = get_user_model()



class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Наименование группы',
            slug='test-slug',
            description='test-description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Текст поста',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Text comment'
        )
        
    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def validate_context(self, response):
        """Проверка полей контекста"""
        self.assertEqual(
            response.context['page_obj'][0].author.username,
            self.post.author.username)
        self.assertEqual(
            response.context['page_obj'][0].text,
            self.post.text)
        self.assertEqual(
            response.context['page_obj'][0].id,
            self.post.id
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.post.image
        )

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.client.get(reverse('posts:index'))
        self.validate_context(response)

    def test_group_posts_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.validate_context(response)
        self.assertEqual(
            response.context['page_obj'][0].group.title, self.group.title)
        self.assertEqual(
            response.context['group'], self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:profile', kwargs={'username': self.author})
        )
        self.validate_context(response)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_page_object = response.context['post']
        self.assertEqual(first_page_object.text, self.post.text)
        self.assertEqual(first_page_object.author, self.author)
        self.assertEqual(first_page_object.group, self.group)
        self.assertEqual(first_page_object.id, self.post.id)
        self.assertEqual(first_page_object.image, self.post.image)

    def test_post_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_new_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIsNone(response.context.get('is_edit', None))

    def test_authorized_can_leave_comment(self):
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
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': self.post.pk}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.author, self.author)

    def test_added_comment_is_on_post_detail_page(self):
        response = self.client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertIn(self.comment, response.context['comments'])

    def test_cache_index_page(self):
        """Тестирование использование кеширования"""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_check = response.content
        post = Post.objects.get(pk=1)
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cache_check)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.authorized_author = Client()
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description',
        )
        for post_index in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Какой-то текст № {post_index}',
                group=cls.group,
            )

    def test_index_first_page_contains_num_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), NUM_OF_POST)

    def test_index_second_page_contains_num_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        second_page = Post.objects.count() % NUM_OF_POST
        self.assertEqual(len(response.context['page_obj']), second_page)

    def test_group_list_first_page_contains_num_records(self):
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), NUM_OF_POST)

    def test_group_list_second_page_contains_num_records(self):
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}) + '?page=2'
        )
        second_page = Post.objects.count() % NUM_OF_POST
        self.assertEqual(len(response.context['page_obj']), second_page)

    def test_profile_first_page_contains_num_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username})
        )
        self.assertEqual(len(response.context['page_obj']), NUM_OF_POST)

    def test_profile_second_page_contains_num_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}) + '?page=2'
        )
        second_page = Post.objects.count() % NUM_OF_POST
        self.assertEqual(len(response.context['page_obj']), second_page)

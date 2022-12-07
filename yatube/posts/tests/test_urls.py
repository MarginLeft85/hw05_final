from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user_no_author = User.objects.create_user(username='another_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост Тестовый пост Тестовый пост',
        )

        cls.urls = (
            ('posts:group_list', (cls.group.slug,),
                f'/group/{cls.group.slug}/'),
            ('posts:index', None, '/',),
            ('posts:group_list', (cls.group.slug,),
                f'/group/{cls.group.slug}/'),
            ('posts:profile', (cls.author.username,),
                f'/profile/{cls.author.username}/'),
            ('posts:post_detail', (cls.post.pk,),
                f'/posts/{cls.post.pk}/'),
            ('posts:post_edit', (cls.post.pk,),
                f'/posts/{cls.post.pk}/edit/'),
            ('posts:post_create', None, '/create/')
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.auth_no_author = Client()
        self.auth_no_author.force_login(self.user_no_author)

    def test_reverse(self):
        """Проверка реверсов."""
        for url, args, hard_link in self.urls:
            reverse_name = reverse(url, args=args)
            with self.subTest(reverse_name=hard_link):
                self.assertEqual(reverse_name, hard_link)

    def test_urls_exists_at_desired_location_for_guest(self):
        """Проверка доступности адресов страниц для гостя."""
        rederict_urls = (
            'posts:post_create',
            'posts:post_edit',
        )
        for url, args, _, in self.urls:
            reverse_name = reverse(url, args=args)
            with self.subTest(reverse_name=reverse_name):
                if url in rederict_urls:
                    response = self.client.get(reverse_name, follow=True)
                    login = reverse(settings.LOGIN_URL)
                    self.assertRedirects(
                        response,
                        f'{login}?{REDIRECT_FIELD_NAME}={reverse_name}',
                        HTTPStatus.FOUND
                    )
                else:
                    response = self.client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_nonexistent_page(self):
        """Проверка 404 для несуществующих страниц."""
        url = '/unexisting_page/'
        roles = (
            self.authorized_client,
            self.auth_no_author,
            self.client,
        )
        for role in roles:
            with self.subTest(url=url):
                response = role.get(url, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_exists_at_desired_location_for_author(self):
        """Проверка доступности адресов страниц для автора."""
        for url, args, _, in self.urls:
            reverse_name = reverse(url, args=args)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_no_authorized_user(self):
        """Проверка ссылок авторизованному пользователю - не автору поста."""
        for url, args, _, in self.urls:
            reverse_name = reverse(url, args=args)
            with self.subTest():
                if reverse_name == reverse(
                        'posts:post_edit',
                        kwargs={'post_id': self.post.id},
                ):
                    response = self.auth_no_author.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    response = self.auth_no_author.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

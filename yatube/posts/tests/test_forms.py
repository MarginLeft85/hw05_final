from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='slagtest_1',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='slagtest_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост 1',
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)

    def test_create_form(self):
        Post.objects.all().delete()
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
            name='small_2.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Новый текст из формы',
            'image': uploaded,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_form_for_guest(self):
        """Проверяем редирект гостя при попытке зайти на страницу /create/."""
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
            name='small_2.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        post_count = Post.objects.count()
        self.assertEqual(
            post_count,
            1,
        )
        form_data_edit = {
            'text': 'Редактируем тестовый пост',
            'group': self.group_2.id,
        }
        response_edit = self.authorized_author.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data_edit,
            follow=True
        )
        self.assertRedirects(
            response_edit,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(
            Post.objects.count(),
            post_count,
        )
        post = Post.objects.first()
        self.assertEqual(
            post.author,
            self.post.author,
        )
        self.assertEqual(
            post.text,
            form_data_edit['text'],
        )
        self.assertEqual(
            post.group.pk,
            form_data_edit['group'],
        )

        self.assertEqual(response_edit.status_code, HTTPStatus.OK)

        response = self.authorized_author.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.NUMS_POSTS_AFTER_EDIT_PAGE)


class CommentFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_auth_user_can_write_comment(self):
        """Комментарии могут оставлять авторизованные пользователи"""
        comments_count = self.post.comments.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), comments_count + 1)
        self.assertTrue(
            self.post.comments.filter(
                text='Новый комментарий',
                author=self.author
            ).exists()
        )
        comment = Comment.objects.first()
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.author)
        self.assertEqual(comment.text, form_data['text'])

    def test_guest_cannot_write_comment(self):
        """Комментарии не могут оставлять гости"""
        comments_count = self.post.comments.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        self.client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(self.post.comments.count(), comments_count)

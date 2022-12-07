from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый постТестовый постТестовый пост',
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        post_obj_name = post.text[:15]
        self.assertEqual(post_obj_name, str(post))

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_verbose_name(self):
        """verbose_name модели Post совпадает с ожидаемыми."""
        post = PostModelTest.post
        verbose_text = post._meta.get_field('text').verbose_name
        verbose_date = post._meta.get_field('pub_date').verbose_name
        verbose_author = post._meta.get_field('author').verbose_name
        verbose_group = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose_text, 'Содержание поста')
        self.assertEqual(verbose_date, 'Дата поста')
        self.assertEqual(verbose_author, 'Автор поста')
        self.assertEqual(verbose_group, 'Сообщество')

    def test_post_help_text(self):
        """help_text модели Post совпадает с ожидаемыми."""
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        help_author = post._meta.get_field('author').help_text
        help_group = post._meta.get_field('group').help_text
        self.assertEqual(help_text, 'Введите текст')
        self.assertEqual(help_author, 'Изменить авторство')
        self.assertEqual(help_group, 'Введите название для группы')

    def test_group_verbose_name(self):
        """verbose_name модели Group совпадает с ожидаемыми."""
        group = PostModelTest.group
        verbose_title = group._meta.get_field('title').verbose_name
        verbose_slug = group._meta.get_field('slug').verbose_name
        verbose_description = group._meta.get_field('description').verbose_name
        self.assertEqual(verbose_title, 'Название группы')
        self.assertEqual(verbose_slug, 'slug')
        self.assertEqual(verbose_description, 'Описание группы')

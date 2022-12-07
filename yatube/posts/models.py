from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200,
        help_text='Введите название для группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug',
        help_text='Имя группы'
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание группы',
        help_text='Краткое описание для кого это группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Содержание поста',
        help_text='Введите текст'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата поста')
    group = models.ForeignKey(
        Group,
        verbose_name="Сообщество",
        help_text="Введите название для группы",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts')
    author = models.ForeignKey(
        User,
        verbose_name="Автор поста",
        help_text='Изменить авторство',
        on_delete=models.CASCADE,
        related_name='posts')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    class Meta:
        ordering = ('-pub_date'),
        verbose_name = 'Пост',
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
        verbose_name="Пост"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name="Автор комментария"
    )
    text = models.TextField("Текст комментария")
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время публикации"
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписались',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

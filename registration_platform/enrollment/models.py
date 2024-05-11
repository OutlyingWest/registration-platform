from django.conf import settings
from django.db import models


class Exam(models.Model):
    title = models.CharField(verbose_name='Название экзамена', max_length=30, unique=True)
    author = models.ManyToManyField(verbose_name='Автор экзамена', to=settings.AUTH_USER_MODEL, db_table='exam_authors',
                                    related_name='author')
    description = models.TextField(verbose_name='Описание экзамена', max_length=200)
    start_date = models.DateField(verbose_name='Дата проведения экзамена')
    duration = models.PositiveIntegerField(verbose_name='Продолжительность экзамена')
    price = models.PositiveIntegerField(verbose_name='Цена', blank=True)

    class Meta:
        verbose_name_plural = 'Экзамены'
        verbose_name = 'Экзамен'
        ordering = ['title']
        # Set permissions for model in format: (<codename>, <name>) where field <name> - comment
        permissions = (
            ('modify_course', 'Can modify course content'),
        )

    def __str__(self):
        return f'{self.title}: Старт {self.start_date}'


class Tracking(models.Model):
    exam = models.ForeignKey(Exam, verbose_name='Экзамен', on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
    passed = models.BooleanField(verbose_name='Пройден?', default=None)

    class Meta:
        ordering = ['-user']


from django.db import models

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (@{self.username})"

class Task(models.Model):
    # Добавляем связь: задача теперь "знает", какому пользователю она принадлежит
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    priority = models.CharField(max_length=20, default='medium')
    deadline = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title
